# JMTFCW-ai
Just Make The Fucking Compiler Work

`example.source` defines the supported statement format:

```
print "Hello, World"
```

Each matching line prints the bytes between the double quotes followed by a
newline. Spaces or tabs may precede the statement, separate `print` from the
quote, or follow the closing quote. Quotes and newlines cannot occur inside
the text; backslashes have no special meaning. Other lines are ignored, not
corrected, so even an empty or arbitrary binary input generates valid C.
The source file is never rewritten.

Install with Python 3.9+ and pip:

```
python -m pip install .
```

Compile and run the example (requires GCC):

```
jmtfcw example.source -o hello
./hello
```

Use `jmtfcw example.source -S -o hello.c` to emit C without invoking GCC.
Without `-o`, the output is `a.out`, or `output.c` with `-S`. The compiler
can also be invoked as `python -m jmtfcw`.
