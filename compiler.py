import re

class BScriptCompiler:
    def __init__(self):
        self.vars = set()
        self.c_lines = []
        self.loop_stack = []
        self.indent_level = 1
        self.str_declared = False

    def indent(self):
        return "    " * self.indent_level

    def compile(self, code: str) -> str:
        lines = self.preprocess(code)
        self.c_lines = [
            '// Generated C code from BScript',
            '#include <stdio.h>',
            '#include <string.h>',
            '',
            'int main() {'
        ]
        # Declare single string buffer
        self.c_lines.append('    char str[256] = "";')
        self.str_declared = True

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line == "":
                i += 1
                continue

            # Comment detection:
            if re.match(r'\s*//', line):
                self.c_lines.append(self.indent() + line.lstrip())
                i += 1
                continue


            # var declaration
            m = re.match(r'var\s+([a-zA-Z_]\w*);', line)
            if m:
                var = m.group(1)
                if var not in self.vars:
                    self.vars.add(var)
                    self.c_lines.append(f'{self.indent()}unsigned char {var} = 0;')
                i += 1
                continue

            # increment/decrement
            m = re.match(r'([a-zA-Z_]\w*)\s*([+-]);', line)
            if m:
                var, op = m.groups()
                if var not in self.vars:
                    raise Exception(f"Variable '{var}' used before declaration")
                if op == '+':
                    self.c_lines.append(f'{self.indent()}{var} = ({var} + 1) % 256;')
                else:
                    self.c_lines.append(f'{self.indent()}{var} = ({var} - 1 + 256) % 256;')
                i += 1
                continue

            # print statements
            m = re.match(r'print\s+(.*);', line)
            if m:
                expr = m.group(1).strip()
                if expr == 'str':
                    self.c_lines.append(f'{self.indent()}printf("%s", str);')
                elif expr in self.vars:
                    self.c_lines.append(f'{self.indent()}printf("%c", {expr});')
                else:
                    # assume string literal with quotes
                    literal = expr.strip('"').strip("'")
                    self.c_lines.append(f'{self.indent()}printf("{literal}");')
                i += 1
                continue

            # str assignment
            m = re.match(r'str\s+"([^"]*)"', line)
            if m:
                content = m.group(1)
                self.c_lines.append(f'{self.indent()}strcpy(str, "{content}");')
                i += 1
                continue

            # input (just fgets from stdin)
            if line == 'input':
                self.c_lines.append(f'{self.indent()}fgets(str, sizeof(str), stdin);')
                i += 1
                continue

            # ascii index to var: ascii 0,a
            m = re.match(r'ascii\s+(\d+),\s*([a-zA-Z_]\w*)', line)
            if m:
                idx, var = m.groups()
                if var not in self.vars:
                    raise Exception(f"Variable '{var}' used before declaration")
                self.c_lines.append(f'{self.indent()}{var} = (unsigned char)str[{idx}];')
                i += 1
                continue

            # revascii var
            m = re.match(r'revascii\s+([a-zA-Z_]\w*)', line)
            if m:
                var = m.group(1)
                if var not in self.vars:
                    raise Exception(f"Variable '{var}' used before declaration")
                # Append char to str
                # We'll do strcat with single char string
                self.c_lines.append(f'{self.indent()}char tmp[2] = {{ (char){var}, \'\\0\' }};')
                self.c_lines.append(f'{self.indent()}strcat(str, tmp);')
                i += 1
                continue

            # loops (a,b) { ... }
            m = re.match(r'\((\w+),\s*(\w+)\)\s*{', line)
            if m:
                var1, var2 = m.groups()
                if var1 not in self.vars or var2 not in self.vars:
                    raise Exception(f"Loop variables must be declared before use")
                self.c_lines.append(f'{self.indent()}while ({var1} != {var2}) {{')
                self.loop_stack.append('}')
                self.indent_level += 1
                i += 1
                continue

            if line == '}':
                if not self.loop_stack:
                    raise Exception("Unexpected closing brace '}'")
                self.indent_level -= 1
                self.c_lines.append(self.indent() + self.loop_stack.pop())
                i += 1
                continue

            raise Exception(f"Unknown or unsupported command: {line}")

        # Close main
        self.c_lines.append('    return 0;')
        self.c_lines.append('}')

        return '\n'.join(self.c_lines)

    def preprocess(self, code: str):
        # Very simple preprocessing: split by lines, remove empty lines and comments
        raw_lines = code.split('\n')
        clean_lines = []
        for line in raw_lines:
            line = line.strip()
            if not line:
                continue
            clean_lines.append(line)
        return clean_lines