import argparse
from compiler import BScriptCompiler
import setup

with open("splash.txt", "r") as f:
    message = f.read()

def main():
    parser = argparse.ArgumentParser(description="BScript Compiler CLI")
    parser.add_argument("--file", help="BScript source file (.bs) (optional)")
    parser.add_argument("--out", "-o", help="Output C file (optional)")
    parser.add_argument("--compile", "-c", help="Compile the C file as an executable (optional)")
    args = parser.parse_args()

    if args.file:
        with open(args.file, "r") as f:
            code = f.read()

        compiler = BScriptCompiler()
        c_code = compiler.transpile(code)

        out_file = args.out if args.out else args.file.rsplit(".", 1)[0] + ".c"
        with open(out_file, "w") as f:
            f.write(c_code)

        if args.compile:
            try:
                compiler.compile("output", args.file)
            except:
                ValueError("Failed to compile. This is some .bs.")

        print(f"C code written to {out_file}")

    else:
        print(message)
        print("\n")
        print("BScript Compiler CLI")
        print("\n")
        print("Usage:")
        print("  --file <file>       BScript source file (.bs) (optional)")
        print("  --out <file>        Output C file (optional)")
        print("  --compile           Compile the C file as an executable (optional)")

if __name__ == "__main__":
    main()
