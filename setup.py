import os

def get_shell_config_file():
    shell = os.environ.get("SHELL", "")
    if "zsh" in shell:
        return "~/.zshrc"
    elif "bash" in shell:
        # On macOS, bash uses ~/.bash_profile by default
        return "~/.bash_profile"
    else:
        # fallback
        return "~/.bashrc"

def append_to_file(file_path, text):
    expanded_path = os.path.expanduser(file_path)
    try:
        with open(expanded_path, "a") as f:
            f.write(text + "\n")
        return True
    except Exception as e:
        print(f"Failed to write to {expanded_path}: {e}")
        return False

def main():
    print("=== BScript Setup Script ===")

    if input("Do you want to setup BScript? (Y/n) ").strip().lower() not in ("", "y", "yes"):
        print("Setup cancelled.")
        return

    if input("This script will only do user-level changes. Proceed? (Y/n) ").strip().lower() not in ("", "y", "yes"):
        print("Setup cancelled.")
        return

    path_correct = False
    while not path_correct:
        path = input("Enter the ABSOLUTE path to your BScript python scripts folder (no trailing slash): ").strip()
        if not path:
            print("Path cannot be empty.")
            continue
        if not os.path.isabs(path):
            print("Please enter an absolute path.")
            continue
        if input(f"Is this path correct? '{path}' (Y/n) ").strip().lower() in ("", "y", "yes"):
            path_correct = True

    config_file = get_shell_config_file()
    print(f"Detected shell config file: {config_file}")

    alias_line = f'alias bsc="python3 {path}/bscript.py"'
    path_line = 'export PATH="$HOME/devtools/bin:$PATH"'

    print(f"Adding alias and PATH export to {config_file}...")

    success_alias = append_to_file(config_file, alias_line)
    success_path = append_to_file(config_file, path_line)

    if success_alias and success_path:
        print(f"\nSetup complete! To start using 'bsc', run:")
        print(f"  source {config_file}")
        print("Or just close and reopen your terminal.")
    else:
        print("There was a problem writing to your shell config file.")

if __name__ == "__main__":
    main()
