import argparse
from compiler import BScriptCompiler

def main():
    parser = argparse.ArgumentParser(description="BScript Compiler CLI")
    parser.add_argument("file", help="BScript source file (.bs)")
    parser.add_argument("--out", "-o", help="Output C file (optional)")
    args = parser.parse_args()

    with open(args.file, "r") as f:
        code = f.read()

    compiler = BScriptCompiler()
    c_code = compiler.compile(code)

    out_file = args.out if args.out else args.file.rsplit(".", 1)[0] + ".c"
    with open(out_file, "w") as f:
        f.write(c_code)

    print(f"C code written to {out_file}")

if __name__ == "__main__":
    main()
