import argparse
from pathlib import Path
import re
import subprocess
import sys
import tempfile


PRINT = re.compile(rb'[ \t]*print[ \t]+"([^"\r\n]*)"[ \t\r]*')


def compile_source(source: bytes) -> str:
    """Translate recognized source lines into a complete C program."""
    lines = ["#include <stdio.h>", "", "int main(void) {"]
    for line in source.split(b"\n"):
        match = PRINT.fullmatch(line)
        if match:
            data = match.group(1) + b"\n"
            values = ", ".join(str(byte) for byte in data)
            lines.append(f"    {{ const unsigned char text[] = {{{values}}};")
            lines.append("      (void)fwrite(text, 1, sizeof text, stdout); }")
    lines.extend(["    return 0;", "}", ""])
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Compile an example-format source file.")
    parser.add_argument("source", type=Path, help="source file to compile")
    parser.add_argument("-o", type=Path, help="output path (default: a.out, or output.c with -S)")
    parser.add_argument("-S", action="store_true", help="emit C without invoking GCC")
    args = parser.parse_args(argv)
    output = args.o or Path("output.c" if args.S else "a.out")

    try:
        if (args.source.resolve() == output.resolve()
                or (args.source.exists() and output.exists() and args.source.samefile(output))):
            parser.error("output must not overwrite the source file")
        c_source = compile_source(args.source.read_bytes())
        if args.S:
            output.write_text(c_source, encoding="ascii")
        else:
            with tempfile.TemporaryDirectory() as directory:
                c_path = Path(directory) / "program.c"
                c_path.write_text(c_source, encoding="ascii")
                result = subprocess.run(["gcc", str(c_path), "-o", str(output)], check=False)
                return result.returncode
    except OSError as error:
        print(f"jmtfcw: {error}", file=sys.stderr)
        return 1
    return 0
