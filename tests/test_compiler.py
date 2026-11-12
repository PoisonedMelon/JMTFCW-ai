import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from jmtfcw.compiler import compile_source


ROOT = Path(__file__).resolve().parents[1]


class CompilerTests(unittest.TestCase):
    def run_compiler(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "jmtfcw", *map(str, args)],
            cwd=ROOT, capture_output=True,
        )

    def test_example_compiles_and_runs(self):
        with tempfile.TemporaryDirectory() as directory:
            binary = Path(directory) / "hello"
            result = self.run_compiler(ROOT / "example.source", "-o", binary)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(subprocess.check_output([binary]), b"Hello, World\n")

    def test_arbitrary_input_emits_valid_c_and_preserves_print_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            source = directory / "input"
            c_file = directory / "output.c"
            binary = directory / "output"
            source.write_bytes(
                b'invalid \xff\nprint "first"\r\nprint ""\n'
                b'print "backslash \\; \x00 \xff"\nprint "unfinished\n'
                b'print "extra" junk\n'
            )
            result = self.run_compiler(source, "-S", "-o", c_file)
            self.assertEqual(result.returncode, 0, result.stderr)
            subprocess.run(["gcc", "-std=c99", "-pedantic-errors", c_file, "-o", binary], check=True)
            self.assertEqual(
                subprocess.check_output([binary]),
                b"first\n\nbackslash \\; \x00 \xff\n",
            )

    def test_empty_and_unrecognized_input_produce_c(self):
        self.assertIn("int main(void)", compile_source(b""))
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input"
            binary = Path(directory) / "output"
            source.write_bytes(b'\xff\x00\nnot a statement\n')
            result = self.run_compiler(source, "-o", binary)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(subprocess.check_output([binary]), b"")

    def test_output_cannot_overwrite_source(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input"
            source.write_bytes(b'print "original"')
            for extra in ([], ["-S"]):
                result = self.run_compiler(source, "-o", source, *extra)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(source.read_bytes(), b'print "original"')

    def test_output_cannot_overwrite_hard_linked_source(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input"
            output = Path(directory) / "output"
            source.write_bytes(b'print "original"')
            os.link(source, output)
            result = self.run_compiler(source, "-S", "-o", output)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(source.read_bytes(), b'print "original"')


if __name__ == "__main__":
    unittest.main()
