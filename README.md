# BScript

BScript is a simple, lightweight 8-bit coding language.

[Read the documentation here.](https://brainy0789.github.io/BScript/basics.html)

## Installation

First of all, install [the latest version of Python](https://www.python.org/downloads/).


Secondly, download the source code from here.

Now, finally, run the `setup.py` file inside of Python. It will ask for things and then you can use the `bsc` command to compile BScript files! Neat!

Or, just download the GUI app if you prefer. It's completely self-contained and required no dependencies.

## Requirements

## SDL2

To compile programs that use the `window;` command in BScript, you need SDL2 installed.

<details>
<summary><strong>Windows</strong></summary>

Using MSYS2:

```bash
pacman -S mingw-w64-x86_64-SDL2
```

Make sure you're using the **MSYS2 MinGW 64-bit** terminal, and that `C:\msys64\mingw64\bin` is in your PATH.

</details>

<details>
<summary><strong>macOS</strong></summary>

Install Homebrew if you haven't already:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Then install SDL2 via Homebrew:

```bash
brew install sdl2
```

</details>

<details>
<summary><strong>Linux (Debian/Ubuntu)</strong></summary>

```bash
sudo apt update
sudo apt install libsdl2-dev
```

</details>

<details>
<summary><strong>Linux (Fedora/RHEL)</strong></summary>

```bash
sudo dnf install SDL2-devel
```

</details>


### GCC Compiler

BScript uses **GCC** (or compatible C compiler) to compile transpiled code. Please ensure it's installed on your system.

<details>
<summary><strong>macOS</strong></summary>

- Install **Xcode Command Line Tools**:
  
```bash
xcode-select --install
```

- This will give you `gcc` (which points to Clang, and works fine for most C programs).
</details>

<details>
<summary><strong>Linux (Debian/Ubuntu/Fedora/Arch)</strong></summary>

- On Debian/Ubuntu:

```bash
sudo apt update
sudo apt install build-essential
```

- On Fedora:

```bash
sudo dnf groupinstall "Development Tools"
```

- On Arch Linux:

```bash
sudo pacman -S base-devel
```

</details>

<details>
<summary><strong>Windows</strong></summary>

#### Option 1: MSYS2 (Recommended)
1. Download and install: [https://www.msys2.org](https://www.msys2.org)
2. Open the **MSYS2 MinGW 64-bit** terminal.
3. Run:

```bash
pacman -S mingw-w64-x86_64-gcc
```

> Make sure to add `C:\msys64\mingw64\bin` to your system PATH.

#### Option 2: MinGW (Standalone)
1. Download from: [https://osdn.net/projects/mingw/releases/](https://osdn.net/projects/mingw/releases/)
2. Select the `mingw32-gcc-g++` package in the installer.
3. Add `C:\MinGW\bin` to your PATH environment variable.

</details>
