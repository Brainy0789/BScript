import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import compiler as c
import os
import tempfile

def transpile_code():
    code = code_input.get("1.0", tk.END)
    compiler = c.BScriptCompiler()
    try:
        c_code = compiler.transpile(code)
        output.delete("1.0", tk.END)
        output.insert(tk.END, c_code)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def save_c_code():
    c_code = output.get("1.0", tk.END)
    if not c_code.strip():
        messagebox.showwarning("Warning", "No C code to save.")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".c", filetypes=[("C Files", "*.c")])
    if file_path:
        with open(file_path, "w") as f:
            f.write(c_code)
        messagebox.showinfo("Saved", f"C code saved to {file_path}")

def load_bs_file():
    file_path = filedialog.askopenfilename(filetypes=[("BScript Files", "*.bs")])
    if file_path:
        with open(file_path, "r") as f:
            code = f.read()
        code_input.delete("1.0", tk.END)
        code_input.insert(tk.END, code)

def compile_c_code():
    c_code = output.get("1.0", tk.END)
    if not c_code.strip():
        messagebox.showwarning("Warning", "No C code to compile.")
        return

    # Save C code to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".c") as tmp_c:
        tmp_c.write(c_code.encode())
        c_file = tmp_c.name

    # Ask user where to save the compiled binary
    output_path = filedialog.asksaveasfilename(defaultextension="", filetypes=[("Executable", "")])
    if not output_path:
        os.remove(c_file)
        return

    compiler = c.BScriptCompiler()
    try:
        compiler.compile(c_file, output_path)
        messagebox.showinfo("Success", f"Compiled successfully to {output_path}")
    except Exception as e:
        messagebox.showerror("Compile Error", str(e))
    finally:
        os.remove(c_file)

root = tk.Tk()
root.title("BScript Compiler GUI")

tk.Button(root, text="Load BScript File", command=load_bs_file).pack(pady=5)

tk.Label(root, text="BScript Code:").pack(anchor="w")
code_input = scrolledtext.ScrolledText(root, width=60, height=15)
code_input.pack(padx=10, pady=5)

tk.Button(root, text="Transpile to C", command=transpile_code).pack(pady=5)

tk.Label(root, text="Generated C Code:").pack(anchor="w")
output = scrolledtext.ScrolledText(root, width=60, height=15)
output.pack(padx=10, pady=5)

tk.Button(root, text="Save C Code", command=save_c_code).pack(pady=5)

tk.Button(root, text="Compile C Code", command=compile_c_code).pack(pady=5)

root.mainloop()