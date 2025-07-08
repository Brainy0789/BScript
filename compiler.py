import re
import subprocess
import shlex

class BScriptCompiler:
    def __init__(self):
        self.global_vars = set()
        self.global_var_decls = []
        self.main_code = []
        self.c_lines = []
        self.loop_stack = []
        self.indent_level = 1
        self.str_declared = False
        self.function_mode = False
        self.in_function = False
        self.current_function = None
        self.functions = {}
        self.block_stack = []  # Track blocks: 'function' or 'loop'
        self.vars = set()  # Local variables in the current function
        self.global_var_decls = []  # store global var declarations

    def indent(self):
        return "    " * self.indent_level

    def add_var(self, var):
        if var not in self.global_vars:
            self.global_vars.add(var)
            decl = f'unsigned char {var} = 0;'
            if self.in_function:
                # local variable inside function
                self.c_lines.append(self.indent() + decl)
            else:
                # global variable declaration (outside main)
                self.global_var_decls.append(decl)

    def transpile_to_js(self, code: str) -> str:
        lines = self.preprocess(code)

        js_lines = [
            '// Generated JavaScript code from BScript',
            ''
            'function print(text) {',
            '    const consoleEl = document.getElementById("console");',
            '    if (consoleEl) {',
            '        consoleEl.textContent += text + "\\n";',
            '    } else {',
            '        // fallback if no custom console',
            '        console.log(text);',
            '    }',
            '}',
            'let str = "";',
            ''
        ]
        global_vars = set()
        local_vars = set()
        functions = {}
        function_mode = False
        current_function = None
        block_stack = []  # 'function' or 'loop'
        indent_level = 0

        def indent():
            return "    " * indent_level

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue

            # Function definition
            m = re.match(r'func\s+(\w+)\s*(.*)\s*{', line)
            if m:
                name, args = m.groups()
                args = [a.strip() for a in args.split(',') if a.strip()]
                function_mode = True
                current_function = name
                functions[name] = {"args": args, "returns": False}
                args_decl = ", ".join(args)
                js_lines.append(f'function {name}({args_decl}) ' + '{')
                indent_level = 1
                local_vars = set(args)
                block_stack.append("function")
                i += 1
                continue

            # End block
            if line == "}":
                if not block_stack:
                    raise Exception("Unexpected closing brace '}'")
                block_type = block_stack.pop()
                indent_level -= 1
                # Insert return 0 if no explicit return
                if block_type == "function":
                    if not functions[current_function]["returns"]:
                        js_lines.append(indent() + 'return 0;')
                    js_lines.append("}")
                    function_mode = False
                    current_function = None
                    local_vars = set()
                else:
                    js_lines.append(indent() + "}")
                i += 1
                continue

            # Return statement
            m = re.match(r'return\s+([a-zA-Z_]\w*);', line)
            if m:
                value = m.group(1)
                if not function_mode:
                    raise Exception("'return' used outside of a function")
                if value not in local_vars and value not in global_vars:
                    raise Exception(f"Variable '{value}' used in return before declaration")
                functions[current_function]["returns"] = True
                js_lines.append(indent() + f'return {value};')
                i += 1
                continue

            # Function call with assignment: outvar = fname args;
            m = re.match(r'([a-zA-Z_]\w*)\s*=\s*(\w+)\s+(.*);', line)
            if m:
                out_var, fname, args_line = m.groups()
                args = [a.strip() for a in args_line.split(',')]
                if fname not in functions:
                    raise Exception(f"Function '{fname}' not defined")
                if len(args) != len(functions[fname]['args']):
                    raise Exception(f"Function '{fname}' requires {len(functions[fname]['args'])} arguments")
                if function_mode:
                    if out_var not in local_vars:
                        local_vars.add(out_var)
                        js_lines.append(indent() + f'let {out_var} = {fname}({", ".join(args)});')
                    else:
                        js_lines.append(indent() + f'{out_var} = {fname}({", ".join(args)});')
                else:
                    if out_var not in global_vars:
                        global_vars.add(out_var)
                        js_lines.insert(1, f'let {out_var} = 0;')
                    js_lines.append(indent() + f'{out_var} = {fname}({", ".join(args)});')
                i += 1
                continue

            # Function call without assignment: fname args;
            m = re.match(r'(\w+)\s+(.*);', line)
            if m:
                fname, args_line = m.groups()
                args = [a.strip() for a in args_line.split(',')]
                if fname in functions:
                    js_lines.append(indent() + f'{fname}({", ".join(args)});')
                    i += 1
                    continue

            # Comment
            if line.startswith("//"):
                js_lines.append(indent() + line)
                i += 1
                continue

            # Variable declaration
            m = re.match(r'var\s+([a-zA-Z_]\w*);', line)
            if m:
                var = m.group(1)
                if function_mode:
                    if var not in local_vars:
                        local_vars.add(var)
                        js_lines.append(indent() + f'let {var} = 0;')
                else:
                    if var not in global_vars:
                        global_vars.add(var)
                        js_lines.insert(1, f'let {var} = 0;')
                i += 1
                continue

            # Assignment (var = value;)
            m = re.match(r'([a-zA-Z_]\w*)\s*=\s*([a-zA-Z_]\w*|\d+);', line)
            if m:
                var, value = m.groups()
                if function_mode:
                    if var not in local_vars:
                        raise Exception(f"Variable '{var}' used before declaration")
                    if value.isdigit():
                        js_lines.append(indent() + f'{var} = {int(value)} % 256;')
                    else:
                        js_lines.append(indent() + f'{var} = {value};')
                else:
                    if var not in global_vars:
                        raise Exception(f"Variable '{var}' used before declaration")
                    if value.isdigit():
                        js_lines.append(indent() + f'{var} = {int(value)} % 256;')
                    else:
                        js_lines.append(indent() + f'{var} = {value};')
                i += 1
                continue

            # Increment/Decrement
            m = re.match(r'([a-zA-Z_]\w*)\s*([+-]);', line)
            if m:
                var, op = m.groups()
                if function_mode:
                    if var not in local_vars:
                        raise Exception(f"Variable '{var}' used before declaration")
                    if op == '+':
                        js_lines.append(indent() + f'{var} = ({var} + 1) % 256;')
                    else:
                        js_lines.append(indent() + f'{var} = ({var} - 1 + 256) % 256;')
                else:
                    if var not in global_vars:
                        raise Exception(f"Variable '{var}' used before declaration")
                    if op == '+':
                        js_lines.append(indent() + f'{var} = ({var} + 1) % 256;')
                    else:
                        js_lines.append(indent() + f'{var} = ({var} - 1 + 256) % 256;')
                i += 1
                continue

            # Print statement
            m = re.match(r'print\s+(.*);', line)
            if m:
                expr = m.group(1).strip()
                if expr == 'str':
                    js_lines.append(indent() + 'print(str);')
                elif expr.isdigit():
                    js_lines.append(indent() + f'print({expr});')
                else:
                    js_lines.append(indent() + f'print({expr});')
                i += 1
                continue

            # String assignment: str "content"
            m = re.match(r'str\s+\"([^\"]*)\"', line)
            if m:
                content = m.group(1)
                js_lines.append(indent() + f'str = "{content}";')
                i += 1
                continue

            # Input (simplified): input
            if line == 'input;':
                js_lines.append(indent() + 'str = prompt("Input:") || "";')
                i += 1
                continue

            # ASCII -> var: ascii index, var
            m = re.match(r'ascii\s+(\d+),\s*([a-zA-Z_]\w*)', line)
            if m:
                idx, var = m.groups()
                if function_mode:
                    if var not in local_vars:
                        local_vars.add(var)
                        js_lines.append(indent() + f'let {var} = 0;')
                    js_lines.append(indent() + f'{var} = str.charCodeAt({idx}) || 0;')
                else:
                    if var not in global_vars:
                        global_vars.add(var)
                        js_lines.insert(1, f'let {var} = 0;')
                    js_lines.append(indent() + f'{var} = str.charCodeAt({idx}) || 0;')
                i += 1
                continue

            # var -> ASCII append: revascii var
            m = re.match(r'revascii\s+([a-zA-Z_]\w*)', line)
            if m:
                var = m.group(1)
                js_lines.append(indent() + f'str += String.fromCharCode({var});')
                i += 1
                continue

            # Loop: (var1, var2) {
            m = re.match(r'\((\w+),\s*(\w+)\)\s*{', line)
            if m:
                var1, var2 = m.groups()
                js_lines.append(indent() + f'while ({var1} != {var2}) ' + '{')
                indent_level += 1
                block_stack.append("loop")
                i += 1
                continue

            # Unknown command
            raise Exception(f"Unknown or unsupported command: {line}")

        # Add global vars declarations at top (if not already inserted)
        # We inserted some at position 1 to keep order for top declarations

        return '\n'.join(js_lines)



    def transpile(self, code: str, lang: str = "c") -> str:
        windowed = False
        lines = self.preprocess(code)
        lang = lang.lower()
        if lang == "c":
            self.c_lines = [
                '// Generated C code from BScript',
                '',
                '#include <stdio.h>',
                '#include <string.h>',
                '#include <SDL.h>',  # Include SDL for windowing
                'SDL_Window* window;',
                'SDL_Renderer* renderer;',
                '',
                # Declare global string variable
                'char str[256] = "";',
                ''
            ]
            self.global_vars.clear()
            self.global_var_decls.clear()
            self.main_code.clear()
            self.function_mode = False
            self.in_function = False
            self.current_function = None
            self.functions.clear()
            self.loop_stack.clear()
            self.indent_level = 1
            self.block_stack.clear()
            self.vars.clear()
            self.draw_code = []
            window_width = 640
            window_height = 480
            window_title = "BScript Window"
            rect = False  # Track if rect command was used
            rects = 0

            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if not line:
                    i += 1
                    continue

                # Function definition
                m = re.match(r'func\s+(\w+)\s*(.*)\s*{', line)
                if m:
                    name, args = m.groups()
                    args = [a.strip() for a in args.split(',') if a.strip()]
                    self.function_mode = True
                    self.in_function = True
                    self.current_function = name
                    self.functions[name] = {"args": args, "returns": False}
                    args_decl = ", ".join("unsigned char " + a for a in args)
                    self.c_lines.append(f'unsigned char {name}({args_decl}) {{')
                    self.indent_level = 1
                    self.vars.clear()  # Clear local vars at function start
                    # Add args as local vars (inside function scope)
                    for arg in args:
                        self.vars.add(arg)  # <-- Add to local vars, NOT global
                    self.block_stack.append("function")
                    i += 1
                    continue

                # End of any block
                if line == "}":
                    if not self.block_stack:
                        raise Exception("Unexpected closing brace '}'")
                    block_type = self.block_stack.pop()
                    self.indent_level -= 1

                    if block_type == "loop":
                        self.c_lines.append(self.indent() + "}")
                    elif block_type == "function":
                        # ensure return if none provided
                        if not self.functions[self.current_function]["returns"]:
                            self.c_lines.append(f'{self.indent()}return 0;')
                        self.c_lines.append("}")
                        self.function_mode = False
                        self.in_function = False
                        self.current_function = None
                        self.vars.clear()  # Clear local vars at function end
                    i += 1
                    continue

                # Return statement
                m = re.match(r'return\s+([a-zA-Z_]\w*);', line)
                if m:
                    value = m.group(1)
                    if not self.function_mode:
                        raise Exception("'return' used outside of a function")
                    if value not in self.global_vars and value not in self.vars:
                        raise Exception(f"Variable '{value}' used in return before declaration")
                    self.functions[self.current_function]["returns"] = True
                    self.c_lines.append(f'{self.indent()}return {value};')
                    i += 1
                    continue

                # Function call with assignment
                m = re.match(r'([a-zA-Z_]\w*)\s*=\s*(\w+)\s+(.*);', line)
                if m:
                    out_var, fname, args = m.groups()
                    args = [a.strip() for a in args.split(',')]
                    if fname not in self.functions:
                        raise Exception(f"Function '{fname}' not defined")
                    if len(args) != len(self.functions[fname]['args']):
                        raise Exception(f"Function '{fname}' requires {len(self.functions[fname]['args'])} arguments")
                    if self.in_function:
                        if out_var not in self.vars:
                            self.vars.add(out_var)
                            self.c_lines.append(f'{self.indent()}unsigned char {out_var} = {fname}({", ".join(args)});')
                        else:
                            self.c_lines.append(f'{self.indent()}{out_var} = {fname}({", ".join(args)});')
                    else:
                        if out_var not in self.global_vars:
                            self.add_var(out_var)
                        self.main_code.append(f'{self.indent()}{out_var} = {fname}({", ".join(args)});')
                    i += 1
                    continue

                # Function call without assignment
                m = re.match(r'(\w+)\s+(.*);', line)
                if m:
                    fname, args = m.groups()
                    args = [a.strip() for a in args.split(',')]
                    if fname in self.functions:
                        if self.in_function:
                            self.c_lines.append(f'{self.indent()}{fname}({", ".join(args)});')
                        else:
                            self.main_code.append(f'{self.indent()}{fname}({", ".join(args)});')
                        i += 1
                        continue

                # Comment
                if re.match(r'\s*//', line):
                    if self.in_function:
                        self.c_lines.append(self.indent() + line.lstrip())
                    else:
                        self.main_code.append(line)
                    i += 1
                    continue

                # Variable declaration
                m = re.match(r'var\s+([a-zA-Z_]\w*);', line)
                if m:
                    var = m.group(1)
                    if self.in_function:
                        if var not in self.vars:
                            self.vars.add(var)
                            self.c_lines.append(f'{self.indent()}unsigned char {var} = 0;')
                    else:
                        self.add_var(var)
                    i += 1
                    continue

                # Assignment
                m = re.match(r'([a-zA-Z_]\w*)\s*=\s*([a-zA-Z_]\w*|\d+);', line)
                if m:
                    var, value = m.groups()
                    if self.in_function:
                        if var not in self.vars:
                            raise Exception(f"Variable '{var}' used before declaration")
                        if value.isdigit():
                            self.c_lines.append(f'{self.indent()}{var} = {int(value)} % 256;')
                        else:
                            self.c_lines.append(f'{self.indent()}{var} = {value};')
                    else:
                        if var not in self.global_vars:
                            raise Exception(f"Variable '{var}' used before declaration")
                        if value.isdigit():
                            self.main_code.append(f'{self.indent()}{var} = {int(value)} % 256;')
                        else:
                            self.main_code.append(f'{self.indent()}{var} = {value};')
                    i += 1
                    continue

                # Increment/Decrement
                m = re.match(r'([a-zA-Z_]\w*)\s*([+-]);', line)
                if m:
                    var, op = m.groups()
                    if self.in_function:
                        if var not in self.vars:
                            raise Exception(f"Variable '{var}' used before declaration")
                        if op == '+':
                            self.c_lines.append(f'{self.indent()}{var} = ({var} + 1) % 256;')
                        else:
                            self.c_lines.append(f'{self.indent()}{var} = ({var} - 1 + 256) % 256;')
                    else:
                        if var not in self.global_vars:
                            raise Exception(f"Variable '{var}' used before declaration")
                        if op == '+':
                            self.main_code.append(f'{self.indent()}{var} = ({var} + 1) % 256;')
                        else:
                            self.main_code.append(f'{self.indent()}{var} = ({var} - 1 + 256) % 256;')
                    i += 1
                    continue

                # Print
                m = re.match(r'print\s+(.*);', line)
                if m:
                    expr = m.group(1).strip()
                    if self.in_function:
                        if expr == 'str':
                            self.c_lines.append(f'{self.indent()}printf("%s", str);')
                        elif expr in self.vars:
                            self.c_lines.append(f'{self.indent()}printf("%d", {expr});')
                        else:
                            literal = expr.strip('"').strip("'")
                            self.c_lines.append(f'{self.indent()}printf("{literal}");')
                    else:
                        if expr == 'str':
                            self.main_code.append(f'{self.indent()}printf("%s", str);')
                        elif expr in self.global_vars:
                            self.main_code.append(f'{self.indent()}printf("%d", {expr});')
                        else:
                            literal = expr.strip('"').strip("'")
                            self.main_code.append(f'{self.indent()}printf("{literal}");')
                    i += 1
                    continue

                # String assignment
                m = re.match(r'str\s+\"([^\"]*)\"', line)
                if m:
                    content = m.group(1)
                    if self.in_function:
                        self.c_lines.append(f'{self.indent()}strcpy(str, "{content}");')
                    else:
                        self.main_code.append(f'{self.indent()}strcpy(str, "{content}");')
                    i += 1
                    continue

                # Input
                if line == 'input;':
                    if self.in_function:
                        self.c_lines.append(f'{self.indent()}fgets(str, sizeof(str), stdin);')
                    else:
                        self.main_code.append(f'{self.indent()}fgets(str, sizeof(str), stdin);')
                    i += 1
                    continue

                # ASCII -> var
                m = re.match(r'ascii\s+(\d+),\s*([a-zA-Z_]\w*)', line)
                if m:
                    idx, var = m.groups()
                    if self.in_function:
                        self.c_lines.append(f'{self.indent()}{var} = (unsigned char)str[{idx}];')
                    else:
                        self.main_code.append(f'{self.indent()}{var} = (unsigned char)str[{idx}];')
                    i += 1
                    continue

                # var -> ASCII
                m = re.match(r'revascii\s+([a-zA-Z_]\w*)', line)
                if m:
                    var = m.group(1)
                    if self.in_function:
                        self.c_lines.append(f'{self.indent()}char tmp[2] = {{ (char){var}, \"\\0\" }};')
                        self.c_lines.append(f'{self.indent()}strcat(str, tmp);')
                    else:
                        self.main_code.append(f'{self.indent()}char tmp[2] = {{ (char){var}, \"\\0\" }};')
                        self.main_code.append(f'{self.indent()}strcat(str, tmp);')
                    i += 1
                    continue

                # Loop
                m = re.match(r'\((\w+),\s*(\w+)\)\s*{', line)
                if m:
                    var1, var2 = m.groups()
                    if self.in_function:
                        self.c_lines.append(f'{self.indent()}while ({var1} != {var2}) {{')
                    else:
                        self.main_code.append(f'{self.indent()}while ({var1} != {var2}) {{')
                    self.indent_level += 1
                    self.block_stack.append("loop")
                    i += 1
                    continue

                # Pixel drawing command
                m = re.match(r'pixel\s+(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+);', line)
                if m:
                    if windowed:
                        x, y, r, g, b, s = map(int, m.groups())
                        rects += 1
                        draw_code = [
                                f'{self.indent()}SDL_SetRenderDrawColor(renderer, {r}, {g}, {b}, 255);',
                                f'{self.indent()}SDL_Rect rect{rects} = {{ {x} * {s}, {y} * {s}, {s}, {s} }};',
                                f'{self.indent()}SDL_RenderFillRect(renderer, &rect{rects});'
                            ]
                        if self.in_function:
                            self.c_lines.extend(draw_code)
                        else:
                            self.draw_code.extend(draw_code)
                    else:
                        raise Exception("Cannot use 'pixel' without first creating a window using the 'window;' command.")
                    i += 1
                    continue

                # rect command
                m = re.match(r'rect\s+(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+);', line)
                if m:
                    if windowed:
                        x, y, wx, wy, r, g, b = map(int, m.groups())
                        rects += 1
                        draw_code = [
                            f'{self.indent()}SDL_SetRenderDrawColor(renderer, {r}, {g}, {b}, 255);',
                            f'{self.indent()}SDL_Rect rect{rects} = {{ {x}, {y}, {wx}, {wy} }};',
                            f'{self.indent()}SDL_RenderFillRect(renderer, &rect{rects});'
                        ]
                        if self.in_function:
                            self.c_lines.extend(draw_code)
                        else:
                            self.draw_code.extend(draw_code)
                    else:
                        raise Exception("Cannot use 'rect' without first creating a window using the 'window;' command.")
                    i += 1
                    continue

                # clearScreen r,g,b;
                m = re.match(r'clearScreen\s+(\d+)\s*,\s*(\d+)\s*,\s*(\d+);', line)
                if m:
                    if not windowed:
                        raise Exception("Cannot use 'clearScreen' without first creating a window using the 'window;' command.")
                    
                    r, g, b = map(int, m.groups())

                    # Clamp RGB values
                    if not all(0 <= val <= 255 for val in (r, g, b)):
                        raise Exception("clearScreen RGB values must be between 0 and 255")

                    draw_code = [
                        f'SDL_SetRenderDrawColor(renderer, {r}, {g}, {b}, 255);',
                        'SDL_RenderClear(renderer);'
                    ]

                    if self.in_function:
                        self.c_lines.extend(f'{self.indent()}{stmt}' for stmt in draw_code)
                    else:
                        self.main_code.extend(f'{self.indent()}{stmt}' for stmt in draw_code)

                    i += 1
                    continue



                # windowSize command
                m = re.match(r'windowSize\s+(\d+)\s*,\s*(\d+);', line)
                if m:
                    width = int(m.group(1))
                    height = int(m.group(2))

                    if not (0 <= width) or not (0 <= height):
                        raise Exception(f"Invalid window size: {width}x{height}. Each dimension must be above 0 pixels.")

                    window_width = width
                    window_height = height
                    i += 1
                    continue


                # windowTitle command
                m = re.match(r'windowTitle\s+"([^"]*)";', line)
                if m:
                    window_title = m.group(1)
                    i += 1
                    continue

                # window command
                if line == 'window;':
                    if windowed:
                        raise Exception("Window already created, cannot create another")
                    windowed = True

                    sdl_code = [
                        "int main(int argc, char* argv[]) {",
                        "    if (SDL_Init(SDL_INIT_VIDEO) != 0) {",
                        "        printf(\"SDL_Init Error: %s\\n\", SDL_GetError());",
                        "        return 1;",
                        "    }",
                        f"    SDL_Window* window = SDL_CreateWindow(\"{window_title}\",",
                        "        SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,",
                        f"        {window_width}, {window_height}, SDL_WINDOW_SHOWN);",
                        "    if (!window) {",
                        "        printf(\"SDL_CreateWindow Error: %s\\n\", SDL_GetError());",
                        "        SDL_Quit();",
                        "        return 1;",
                        "    }",
                        "    SDL_Renderer* renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);",
                        "    if (!renderer) {",
                        "        printf(\"SDL_CreateRenderer Error: %s\\n\", SDL_GetError());",
                        "        SDL_DestroyWindow(window);",
                        "        SDL_Quit();",
                        "        return 1;",
                        "    }",
                        "    SDL_Event e;",
                        "    int running = 1;",
                        "    while (running) {",
                        "        while (SDL_PollEvent(&e)) {",
                        "            if (e.type == SDL_QUIT) {",
                        "                running = 0;",
                        "            }",
                        "        }",
                        "        SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255);",
                        "        SDL_RenderClear(renderer);",
                        "        // Begin drawing section",
                        "        // <-- BScript pixel draw commands go here -->"
                    ]
                    sdl_code2 = [
                        "        // End drawing section",
                        "        SDL_RenderPresent(renderer);",
                        "        SDL_Delay(16);",
                        "    }",
                        "    SDL_DestroyRenderer(renderer);",
                        "    SDL_DestroyWindow(window);",
                        "    SDL_Quit();"
                    ]

                   #if self.in_function:
                    #self.c_lines.extend(f'{self.indent()}{stmt}' for stmt in sdl_code)
                    #else:
                    #    self.main_code.extend(f'{self.indent()}{stmt}' for stmt in sdl_code)
                    i += 1
                    continue

                raise Exception(f"Unknown or unsupported command: {line}")

            # Compose full output
            # Globals first
            output = self.c_lines + self.global_var_decls

            # Then main function

            if not windowed:
                output.append("int main() {")
                output.extend(self.main_code)
                output.append("    return 0;")
                output.append("}")
            else:
                output.extend(sdl_code)
                # If windowed, we already have the main function in sdl_code
                output.extend(self.draw_code)
                output.append("        // End of BScript pixel draw commands")
                output.extend(self.main_code)
                output.extend(sdl_code2)
                output.append("}")

            return '\n'.join(output)
        elif lang == "js":
            return self.transpile_to_js(code)
        else:
            raise NotImplementedError(f"Language '{lang}' not supported yet")

    def preprocess(self, code: str):
        return [line.strip() for line in code.split('\n') if line.strip()]
    
    def compile(self, source_file: str, output_name: str):
        if not output_name or not source_file:
            raise ValueError("Source file and output name must be provided")
        
        # Read the source to check if it uses SDL
        with open(source_file, 'r', encoding='utf-8') as f:
            source_code = f.read()

        # Determine if SDL is needed
        uses_sdl = 'SDL_CreateWindow' in source_code or 'window;' in source_code

        # Set up compilation command
        compile_cmd = ["gcc", source_file, "-o", output_name]

        if uses_sdl:
            try:
                # Get SDL compiler flags safely
                sdl_flags = subprocess.check_output(["sdl2-config", "--cflags", "--libs"])
                compile_cmd += shlex.split(sdl_flags.decode())
            except subprocess.CalledProcessError:
                raise RuntimeError("Failed to retrieve SDL2 compiler flags via sdl2-config")

        # Run compilation
        try:
            subprocess.run(compile_cmd, check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Compilation failed: {e}")
        
        print(f"Compiled {source_file} to {output_name}")
