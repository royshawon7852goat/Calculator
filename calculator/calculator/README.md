# Simple Calculator GUI Application

A modern, elegant, and functional desktop calculator application built for Windows using Python and Tkinter. It features a sleek dark mode user interface, responsive canvas-based rounded buttons, full physical keyboard/numpad support, expression validation, and a 100% safe Abstract Syntax Tree (AST) mathematical parser that eliminates the security risks of `eval()`.

---

## 📸 Interface Preview & Layout

```
+-----------------------------------+
|  Simple Calculator                |
+-----------------------------------+
|                          12 + 5 = | <- History Preview
|                                17 | <- Main Readout
+-----------------------------------+
|  [ AC ]   [ DEL ]  [ +/- ]  [ ÷ ] |
|  [  7 ]   [  8  ]  [  9  ]  [ × ] |
|  [  4 ]   [  5  ]  [  6  ]  [ - ] |
|  [  1 ]   [  2  ]  [  3  ]  [ + ] |
|  [      0      ]   [  .  ]  [ = ] | <- Highlighted '='
+-----------------------------------+
```

---

## ✨ Features

- **Core Operations**: Addition (`+`), Subtraction (`-`), Multiplication (`×`), and Division (`÷`).
- **Precision & Numbers**:
  - Full decimal number support with floating-point cleanup (e.g., `0.1 + 0.2 = 0.3`).
  - Positive and negative number toggle (`+/-`).
  - Standard mathematical operator precedence (BODMAS / PEMDAS).
- **Safe Parsing (No `eval()`)**:
  - Implements Python's built-in `ast` (Abstract Syntax Tree) module to restrict parsing strictly to arithmetic expressions and numeric constants.
  - Malicious calls (`__import__`, `os.system`, file reading) are strictly blocked.
- **Input Validation**:
  - Prevents multiple decimal points in a single number (e.g., `3.14.5` is prohibited).
  - Automatically replaces operators if consecutive operators are entered (e.g., typing `+` then `×` seamlessly updates to `×`).
  - Prevents invalid operator combinations and malformed expressions.
- **Error Handling**:
  - Gracefully captures and displays division by zero (`Cannot divide by zero`) without crashing the application.
- **Modern Dark UI**:
  - Dark charcoal theme with contrasting visual hierarchy.
  - High-DPI scaling enabled for crisp fonts and graphics on 1080p, 2K, and 4K displays.
  - Rounded button components drawn on Tkinter Canvas with smooth hover transitions and click feedback.
  - Highlighted amber/orange equal button for fast visual recognition.
  - Responsive layout that dynamically adjusts when resized.
- **Keyboard & Numpad Support**:
  - Full support for keyboard input with animated button flashes for visual feedback.

---

## ⌨️ Keyboard Shortcuts

| Key | Calculator Action |
| :--- | :--- |
| `0` - `9` (Keyboard & Numpad) | Enter Digits |
| `+` | Addition |
| `-` | Subtraction |
| `*`, `x`, `X` | Multiplication (`×`) |
| `/` | Division (`÷`) |
| `.`, `,` | Decimal Point |
| `Enter`, `KP_Enter`, `=` | Calculate Result (`=`) |
| `Backspace` | Delete Last Character (`DEL`) |
| `Escape`, `c`, `C` | Clear All (`AC`) |
| `F9`, `n`, `N` | Toggle Positive / Negative (`+/-`) |

---

## 📁 Project Structure

```text
calculator/
│
├── main.py              # Main application source code and GUI controller
├── requirements.txt     # Dependency specification (Standard library runtime)
├── test_calculator.py   # Comprehensive automated test suite
└── README.md            # Documentation and instructions
```

---

## 🚀 Running the Application in VS Code (PowerShell)

### Prerequisites
- Python 3.8 or later installed on Windows.
- Tkinter is included automatically with standard Python for Windows installations.

### Step 1: Open VS Code Terminal
1. Open Visual Studio Code.
2. Open the terminal panel (`Ctrl` + `~` or via menu **Terminal > New Terminal**).
3. Ensure the terminal shell is **PowerShell**.

### Step 2: Navigate to the Project Directory
```powershell
cd C:\Users\roysh\.gemini\antigravity\scratch\calculator
```

### Step 3: Launch the Application
Run the main script with Python:
```powershell
python main.py
```

The calculator window will appear on your screen.

---

## 🧪 Running Automated Tests

A dedicated test suite is included to verify all arithmetic operations, edge cases, error conditions, and UI state flows:

```powershell
python test_calculator.py
```

Expected output:
```text
Ran 18 tests in 0.4s
OK
```

---

## 📦 Converting into a Standalone Windows EXE (PyInstaller)

You can package the application into a single `.exe` file that runs on any Windows machine without requiring Python to be installed.

### Step 1: Install PyInstaller
In your VS Code PowerShell terminal, install PyInstaller:
```powershell
pip install pyinstaller
```

### Step 2: Build the Executable
Run the following build command:
```powershell
pyinstaller --onefile --noconsole --name "SimpleCalculator" main.py
```

**Flag Explanations**:
- `--onefile`: Bundles the entire application and its runtime into a single standalone executable.
- `--noconsole`: Suppresses the background Windows command-prompt console window when the GUI is launched.
- `--name "SimpleCalculator"`: Sets the output filename to `SimpleCalculator.exe`.

### Step 3: Run Your Executable
Once the build completes:
1. Open the generated `dist` folder:
   ```powershell
   cd dist
   ```
2. Run the executable:
   ```powershell
   .\SimpleCalculator.exe
   ```
You can now distribute `SimpleCalculator.exe` to any Windows computer!

---

## 🛡️ Security Note: Why No `eval()`?

Standard tutorials often use `eval(expression)` to evaluate calculator input. However, `eval()` executes arbitrary Python code, exposing applications to severe security vulnerabilities (code injection, unauthorized file access, or system command execution).

This calculator employs an AST-based recursive evaluation engine:
```python
tree = ast.parse(sanitized_expression, mode='eval')
```
The engine traverses the syntax tree and strictly validates that every node is:
- A numeric constant (`ast.Constant`), or
- A safe binary operation (`ast.Add`, `ast.Sub`, `ast.Mult`, `ast.Div`), or
- A safe unary operation (`ast.UAdd`, `ast.USub`).

Any other construct (function calls, attribute lookups, loops, imports) is immediately rejected with an exception.
