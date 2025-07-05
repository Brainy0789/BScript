import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import compiler as c
import os
import tempfile
import subprocess

def transpile_code():
    code = code_input.get("1.0", tk.END)
    lang = lang_var.get()
    compiler = c.BScriptCompiler()
    try:
        output_code = compiler.transpile(code, lang=lang)
        output.delete("1.0", tk.END)
        output.insert(tk.END, output_code)
    except NotImplementedError as nie:
        messagebox.showerror("Not Supported", str(nie))
    except Exception as e:
        messagebox.showerror("Error", str(e))

def save_code():
    code = output.get("1.0", tk.END)
    if not code.strip():
        messagebox.showwarning("Warning", "No code to save.")
        return
    ext = ".c" if lang_var.get() == "c" else ".js"
    file_path = filedialog.asksaveasfilename(defaultextension=ext, filetypes=[(f"{lang_var.get().upper()} Files", f"*{ext}")])
    if file_path:
        with open(file_path, "w") as f:
            f.write(code)
        messagebox.showinfo("Saved", f"Code saved to {file_path}")

def load_bs_file():
    file_path = filedialog.askopenfilename(filetypes=[("BScript Files", "*.bs")])
    if file_path:
        with open(file_path, "r") as f:
            code = f.read()
        code_input.delete("1.0", tk.END)
        code_input.insert(tk.END, code)

def compile_js_code(js_code):
    # Ask user to select folder to save index.html and script.js
    folder = filedialog.askdirectory(title="Select folder to save JS app")
    if not folder:
        return

    script_path = os.path.join(folder, "script.js")
    index_path = os.path.join(folder, "index.html")

    # Write script.js
    with open(script_path, "w") as f:
        f.write(js_code)

    # Write index.html that links script.js
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>BScript JS Output</title>
</head>
<body>
<script src="script.js"></script>
</body>
</html>
"""
    with open(index_path, "w") as f:
        f.write(html_content)

    messagebox.showinfo("Success", f"JS app saved:\n{index_path}\n{script_path}")


def compile_code():
    lang = lang_var.get()
    code = output.get("1.0", tk.END).strip()
    if not code:
        messagebox.showwarning("Warning", "No code to compile.")
        return

    if lang == "c":
        # Your existing C compile code here...
        with tempfile.NamedTemporaryFile(delete=False, suffix=".c") as tmp_c:
            tmp_c.write(code.encode())
            c_file = tmp_c.name

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

    elif lang == "js":
        compile_js_code(code)

    else:
        messagebox.showwarning("Compile Not Supported", f"Compile not supported for language: {lang}")


root = tk.Tk()
root.title("BScript Compiler GUI")

tk.Button(root, text="Load BScript File", command=load_bs_file).pack(pady=5)

tk.Label(root, text="BScript Code:").pack(anchor="w")
code_input = scrolledtext.ScrolledText(root, width=60, height=15)
code_input.pack(padx=10, pady=5)

tk.Label(root, text="Select Output Language:").pack(anchor="w", padx=10)
lang_var = tk.StringVar(value="c")
lang_dropdown = tk.OptionMenu(root, lang_var, "c", "js")
lang_dropdown.pack(padx=10, pady=5)

tk.Button(root, text="Transpile to Selected Language", command=transpile_code).pack(pady=5)

tk.Label(root, text="Generated Code:").pack(anchor="w")
output = scrolledtext.ScrolledText(root, width=60, height=15)
output.pack(padx=10, pady=5)

tk.Button(root, text="Save Code", command=save_code).pack(pady=5)

tk.Button(root, text="Compile C Code", command=compile_code).pack(pady=5)

root.mainloop()
