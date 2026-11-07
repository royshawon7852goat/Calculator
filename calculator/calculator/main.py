"""
Simple Calculator GUI Application
=================================
A modern, functional desktop calculator built with Python and Tkinter.

Features:
- Arithmetic operations: Addition, Subtraction, Multiplication, Division
- Decimal numbers and negative numbers support
- Safe mathematical expression parser (no eval)
- Clear All (AC) and Delete (DEL) operations
- Division by zero error handling
- Expression validation (prevents multiple decimals, invalid operator sequences)
- Sleek dark theme with rounded-style buttons and responsive grid layout
- Full physical keyboard and numeric keypad support
"""

import ast
import operator
import re
import sys
import tkinter as tk
from tkinter import font as tkfont


# ==============================================================================
# Safe Expression Evaluation (No eval())
# ==============================================================================

# Whitelisted operators for safe arithmetic AST evaluation
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def evaluate_ast_node(node):
    """
    Recursively evaluate an AST node strictly restricted to numeric constants,
    whitelisted binary operations, and unary operations.
    
    Raises:
        ZeroDivisionError: When division by zero is attempted.
        ValueError: When an unsafe or unsupported AST node is encountered.
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value

    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in SAFE_OPERATORS:
            raise ValueError(f"Unsupported binary operator: {op_type.__name__}")
        left_val = evaluate_ast_node(node.left)
        right_val = evaluate_ast_node(node.right)
        return SAFE_OPERATORS[op_type](left_val, right_val)

    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in SAFE_OPERATORS:
            raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
        operand_val = evaluate_ast_node(node.operand)
        return SAFE_OPERATORS[op_type](operand_val)

    raise ValueError(f"Unsafe or invalid syntax element: {type(node).__name__}")


def safe_calculate(expression: str) -> float:
    """
    Safely evaluate a mathematical expression string using Python's AST parser.
    Converts display symbols '×' and '÷' into valid Python syntax '*' and '/'.
    """
    sanitized = expression.replace("×", "*").replace("÷", "/")
    # Parse in 'eval' mode (single expression only, no statements, imports, loops)
    tree = ast.parse(sanitized.strip(), mode="eval")
    return evaluate_ast_node(tree.body)


def format_result(value: float) -> str:
    """
    Format a floating-point result into a clean, human-friendly string.
    Removes trailing zeros and avoids floating-point precision artifacts.
    """
    if abs(value) < 1e-15:
        return "0"

    # Check if value is effectively an integer
    if abs(value - round(value)) < 1e-12:
        return str(int(round(value)))

    # Format float up to 10 decimal places, stripping trailing zeroes
    formatted = f"{value:.10f}".rstrip("0").rstrip(".")

    # Handle scientific notation or excessively long strings
    if len(formatted) > 14 or "e" in str(value).lower():
        formatted = f"{value:.10g}"

    return formatted


# ==============================================================================
# Modern Rounded Button Widget (Tkinter Canvas)
# ==============================================================================

class RoundedButton(tk.Canvas):
    """
    Custom rounded button component drawn on a Tkinter Canvas.
    Provides smooth corner curves, hover effects, click animations, and
    automatic responsive redraw upon resizing.
    """

    def __init__(
        self,
        parent,
        text: str,
        command=None,
        radius: int = 18,
        bg_color: str = "#2e2f38",
        fg_color: str = "#ffffff",
        hover_color: str = "#3c3e4a",
        active_color: str = "#4a4c5a",
        font=("Segoe UI", 15, "bold"),
        **kwargs,
    ):
        super().__init__(
            parent,
            highlightthickness=0,
            bg=parent["bg"],
            cursor="hand2",
            **kwargs,
        )
        self.radius = radius
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.hover_color = hover_color
        self.active_color = active_color
        self.current_bg = bg_color
        self.command = command
        self.text = text
        self.font = font

        self.polygon_id = None
        self.text_id = None
        self.is_pressed = False

        self.bind("<Configure>", self._on_resize)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _draw(self):
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 10 or h < 10:
            return

        r = min(self.radius, w // 2, h // 2)
        x1, y1, x2, y2 = 2, 2, w - 2, h - 2

        # 20-point rounded rectangle polygon with smooth bezier interpolation
        points = [
            x1 + r, y1,
            x1 + r, y1,
            x2 - r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1 + r,
            x1, y1,
        ]

        if self.polygon_id is None:
            self.polygon_id = self.create_polygon(points, fill=self.current_bg, smooth=True)
            self.text_id = self.create_text(
                w // 2, h // 2, text=self.text, fill=self.fg_color, font=self.font
            )
        else:
            self.coords(self.polygon_id, *points)
            self.itemconfig(self.polygon_id, fill=self.current_bg)
            self.coords(self.text_id, w // 2, h // 2)

    def _on_resize(self, _event):
        self._draw()

    def _on_enter(self, _event):
        if not self.is_pressed:
            self.current_bg = self.hover_color
            if self.polygon_id:
                self.itemconfig(self.polygon_id, fill=self.current_bg)

    def _on_leave(self, _event):
        self.is_pressed = False
        self.current_bg = self.bg_color
        if self.polygon_id:
            self.itemconfig(self.polygon_id, fill=self.current_bg)

    def _on_press(self, _event):
        self.is_pressed = True
        self.current_bg = self.active_color
        if self.polygon_id:
            self.itemconfig(self.polygon_id, fill=self.current_bg)

    def _on_release(self, event):
        if self.is_pressed:
            self.is_pressed = False
            self.current_bg = self.hover_color
            if self.polygon_id:
                self.itemconfig(self.polygon_id, fill=self.current_bg)
            # Only trigger if the release occurs within the button boundaries
            if 0 <= event.x <= self.winfo_width() and 0 <= event.y <= self.winfo_height():
                if self.command:
                    self.command()

    def flash(self, duration_ms: int = 120):
        """Visually flash the button to give instant feedback on keyboard presses."""
        self.current_bg = self.active_color
        if self.polygon_id:
            self.itemconfig(self.polygon_id, fill=self.current_bg)

        def _restore():
            self.current_bg = self.bg_color
            if self.polygon_id:
                self.itemconfig(self.polygon_id, fill=self.current_bg)

        self.after(duration_ms, _restore)


# ==============================================================================
# Main Calculator Application Class
# ==============================================================================

class Calculator:
    """
    Main application controller managing state, user interface, input validation,
    and event handling.
    """

    # UI Theme Palette
    COLOR_BG = "#17171c"
    COLOR_DISPLAY_BG = "#17171c"
    COLOR_DISPLAY_FG = "#ffffff"
    COLOR_HISTORY_FG = "#9ca3af"

    # Number buttons (0-9, .)
    COLOR_NUM_BG = "#2e2f38"
    COLOR_NUM_HOVER = "#3c3e4a"
    COLOR_NUM_ACTIVE = "#4a4c5a"
    COLOR_NUM_FG = "#ffffff"

    # Function buttons (AC, DEL, +/-)
    COLOR_FUNC_BG = "#3e414e"
    COLOR_FUNC_HOVER = "#4e5162"
    COLOR_FUNC_ACTIVE = "#5e6276"
    COLOR_FUNC_FG = "#f3f4f6"

    # Operator buttons (÷, ×, -, +)
    COLOR_OP_BG = "#4b5563"
    COLOR_OP_HOVER = "#5b6575"
    COLOR_OP_ACTIVE = "#6b7587"
    COLOR_OP_FG = "#ffffff"

    # Equal button (=) - highlighted
    COLOR_EQUAL_BG = "#f59e0b"
    COLOR_EQUAL_HOVER = "#fbbf24"
    COLOR_EQUAL_ACTIVE = "#d97706"
    COLOR_EQUAL_FG = "#ffffff"

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Simple Calculator")
        self.root.geometry("350x500")
        self.root.minsize(320, 460)
        self.root.configure(bg=self.COLOR_BG)

        # Enable High-DPI scaling on Windows systems
        self._enable_high_dpi()

        # Application state
        self.expression = ""          # Running expression being evaluated
        self.display_text = "0"       # What is currently visible on the primary readout
        self.history_text = ""       # Calculation preview/history
        self.has_result = False       # Tracks if current screen text is a completed result
        self.is_error = False         # Tracks if calculator is currently in error state

        # Button widget dictionary for keyboard shortcut animations
        self.button_widgets = {}

        # Build GUI components
        self._create_display()
        self._create_buttons()
        self._bind_keyboard_events()

    def _enable_high_dpi(self):
        """Set DPI awareness for crisp font and UI rendering on modern Windows monitors."""
        try:
            if sys.platform == "win32":
                from ctypes import windll
                windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass

    def _create_display(self):
        """Construct the top display screen with secondary history and primary readout."""
        display_frame = tk.Frame(self.root, bg=self.COLOR_DISPLAY_BG, padx=20, pady=16)
        display_frame.pack(fill="x", side="top")

        # Secondary history readout (shows ongoing formula or previous calculation)
        self.history_label = tk.Label(
            display_frame,
            text="",
            anchor="e",
            font=("Segoe UI", 12),
            bg=self.COLOR_DISPLAY_BG,
            fg=self.COLOR_HISTORY_FG,
        )
        self.history_label.pack(fill="x", side="top", pady=(0, 4))

        # Primary readout (shows current number, formula, or result)
        self.display_label = tk.Label(
            display_frame,
            text=self.display_text,
            anchor="e",
            font=("Segoe UI", 28, "bold"),
            bg=self.COLOR_DISPLAY_BG,
            fg=self.COLOR_DISPLAY_FG,
        )
        self.display_label.pack(fill="x", side="top")

    def _update_display(self):
        """Update display labels and dynamically scale down font if text is very long."""
        self.history_label.config(text=self.history_text)
        self.display_label.config(text=self.display_text)

        # Dynamic font scaling to ensure long numbers fit comfortably
        text_length = len(self.display_text)
        if text_length > 18:
            new_size = 18
        elif text_length > 14:
            new_size = 22
        elif text_length > 10:
            new_size = 24
        else:
            new_size = 28

        self.display_label.config(font=("Segoe UI", new_size, "bold"))

    def _create_buttons(self):
        """Construct the responsive grid of buttons."""
        buttons_frame = tk.Frame(self.root, bg=self.COLOR_BG, padx=12, pady=10)
        buttons_frame.pack(fill="both", expand=True, side="bottom")

        # Configure responsive rows and columns
        for row_idx in range(5):
            buttons_frame.rowconfigure(row_idx, weight=1)
        for col_idx in range(4):
            buttons_frame.columnconfigure(col_idx, weight=1)

        # Button Layout Grid:
        # [ AC ]  [ DEL ]  [ +/- ]  [ ÷ ]
        # [  7 ]  [  8  ]  [  9  ]  [ × ]
        # [  4 ]  [  5  ]  [  6  ]  [ - ]
        # [  1 ]  [  2  ]  [  3  ]  [ + ]
        # [    0 (span 2)   ]  [ . ]  [ = ]

        button_configs = [
            # Row 0
            {"text": "AC",  "row": 0, "col": 0, "type": "func", "cmd": self.clear_all},
            {"text": "DEL", "row": 0, "col": 1, "type": "func", "cmd": self.delete_char},
            {"text": "+/-", "row": 0, "col": 2, "type": "func", "cmd": self.toggle_sign},
            {"text": "÷",   "row": 0, "col": 3, "type": "op",   "cmd": lambda: self.append_operator("÷")},

            # Row 1
            {"text": "7",   "row": 1, "col": 0, "type": "num",  "cmd": lambda: self.append_digit("7")},
            {"text": "8",   "row": 1, "col": 1, "type": "num",  "cmd": lambda: self.append_digit("8")},
            {"text": "9",   "row": 1, "col": 2, "type": "num",  "cmd": lambda: self.append_digit("9")},
            {"text": "×",   "row": 1, "col": 3, "type": "op",   "cmd": lambda: self.append_operator("×")},

            # Row 2
            {"text": "4",   "row": 2, "col": 0, "type": "num",  "cmd": lambda: self.append_digit("4")},
            {"text": "5",   "row": 2, "col": 1, "type": "num",  "cmd": lambda: self.append_digit("5")},
            {"text": "6",   "row": 2, "col": 2, "type": "num",  "cmd": lambda: self.append_digit("6")},
            {"text": "-",   "row": 2, "col": 3, "type": "op",   "cmd": lambda: self.append_operator("-")},

            # Row 3
            {"text": "1",   "row": 3, "col": 0, "type": "num",  "cmd": lambda: self.append_digit("1")},
            {"text": "2",   "row": 3, "col": 1, "type": "num",  "cmd": lambda: self.append_digit("2")},
            {"text": "3",   "row": 3, "col": 2, "type": "num",  "cmd": lambda: self.append_digit("3")},
            {"text": "+",   "row": 3, "col": 3, "type": "op",   "cmd": lambda: self.append_operator("+")},

            # Row 4 (0 spans columns 0 and 1)
            {"text": "0",   "row": 4, "col": 0, "colspan": 2, "type": "num", "cmd": lambda: self.append_digit("0")},
            {"text": ".",   "row": 4, "col": 2, "type": "num",  "cmd": self.append_decimal},
            {"text": "=",   "row": 4, "col": 3, "type": "equal", "cmd": self.calculate_result},
        ]

        for cfg in button_configs:
            btn_type = cfg["type"]
            colspan = cfg.get("colspan", 1)

            if btn_type == "num":
                bg = self.COLOR_NUM_BG
                hover = self.COLOR_NUM_HOVER
                active = self.COLOR_NUM_ACTIVE
                fg = self.COLOR_NUM_FG
                btn_font = ("Segoe UI", 16, "bold")
            elif btn_type == "func":
                bg = self.COLOR_FUNC_BG
                hover = self.COLOR_FUNC_HOVER
                active = self.COLOR_FUNC_ACTIVE
                fg = self.COLOR_FUNC_FG
                btn_font = ("Segoe UI", 14, "bold")
            elif btn_type == "op":
                bg = self.COLOR_OP_BG
                hover = self.COLOR_OP_HOVER
                active = self.COLOR_OP_ACTIVE
                fg = self.COLOR_OP_FG
                btn_font = ("Segoe UI", 18, "bold")
            else:  # 'equal'
                bg = self.COLOR_EQUAL_BG
                hover = self.COLOR_EQUAL_HOVER
                active = self.COLOR_EQUAL_ACTIVE
                fg = self.COLOR_EQUAL_FG
                btn_font = ("Segoe UI", 18, "bold")

            btn = RoundedButton(
                buttons_frame,
                text=cfg["text"],
                command=cfg["cmd"],
                radius=18,
                bg_color=bg,
                fg_color=fg,
                hover_color=hover,
                active_color=active,
                font=btn_font,
            )
            btn.grid(
                row=cfg["row"],
                column=cfg["col"],
                columnspan=colspan,
                padx=5,
                pady=5,
                sticky="nsew",
            )
            self.button_widgets[cfg["text"]] = btn

    # ==========================================================================
    # Button Operation Logic
    # ==========================================================================

    def _get_current_number_token(self) -> str:
        """Extract the current trailing number token being entered."""
        # Split on operators: +, -, ×, ÷, and parentheses
        tokens = re.split(r"[+\-×÷()]", self.expression)
        return tokens[-1] if tokens else ""

    def append_digit(self, digit: str):
        """Append a numeric digit (0-9) to the current expression."""
        if self.is_error or self.has_result:
            # Starting fresh after a calculation result or error
            self.expression = digit
            self.display_text = digit
            self.has_result = False
            self.is_error = False
        else:
            if self.expression == "0":
                self.expression = digit
                self.display_text = digit
            else:
                self.expression += digit
                self.display_text = self.expression

        self._update_display()

    def append_operator(self, op: str):
        """
        Append an arithmetic operator (+, -, ×, ÷).
        Prevents consecutive invalid operators by replacing the last operator.
        """
        if self.is_error:
            return

        if self.has_result:
            # Chain calculation starting with previous result
            self.has_result = False

        if not self.expression or self.expression == "0":
            # If empty, only subtraction can start a negative number
            if op == "-":
                self.expression = "-"
                self.display_text = "-"
                self._update_display()
            return

        # Check if the expression currently ends with an operator (with surrounding spaces)
        ends_with_op = re.search(r"\s[+\-×÷]\s$", self.expression)

        if ends_with_op:
            # Replace previous operator with the newly chosen operator
            self.expression = self.expression[:ends_with_op.start()] + f" {op} "
        elif self.expression.endswith("-") and len(self.expression) == 1:
            # Only negative sign exists, do nothing
            return
        else:
            # Normal append with spacing for clean readability
            self.expression += f" {op} "

        self.display_text = self.expression
        self._update_display()

    def append_decimal(self):
        """Append a decimal point, strictly preventing multiple decimals in one number."""
        if self.is_error or self.has_result:
            self.expression = "0."
            self.display_text = "0."
            self.has_result = False
            self.is_error = False
            self._update_display()
            return

        curr_token = self._get_current_number_token().strip()

        # Prevent multiple decimal points within the same numeric token
        if "." in curr_token:
            return

        if not self.expression or self.expression.endswith(" "):
            # Automatically prepend '0' if starting after an operator or empty
            self.expression += "0."
        else:
            self.expression += "."

        self.display_text = self.expression
        self._update_display()

    def toggle_sign(self):
        """Toggle positive/negative sign of the currently active number."""
        if self.is_error:
            return

        if not self.expression or self.expression == "0":
            return

        # Match either a standalone negative number in parentheses e.g. (-12.5)
        # or a standard number at the end of the expression
        paren_neg_match = re.search(r"\(-(\d+(?:\.\d+)?)\)$", self.expression)
        if paren_neg_match:
            # Convert (-X) back to positive X
            val = paren_neg_match.group(1)
            self.expression = self.expression[:paren_neg_match.start()] + val
            self.display_text = self.expression
            self._update_display()
            return

        # Check if the entire expression is just a negative number: -X
        single_neg_match = re.match(r"^-(\d+(?:\.\d+)?)$", self.expression)
        if single_neg_match:
            val = single_neg_match.group(1)
            self.expression = val
            self.display_text = val
            self._update_display()
            return

        # Check for trailing positive number
        pos_match = re.search(r"(\d+(?:\.\d+)?)$", self.expression)
        if pos_match:
            val = pos_match.group(1)
            prefix = self.expression[:pos_match.start()]
            if not prefix:
                # Top level number: turn into -val
                self.expression = f"-{val}"
            else:
                # Sub-expression: wrap safely as (-val)
                self.expression = f"{prefix}(-{val})"
            self.display_text = self.expression
            self._update_display()

    def delete_char(self):
        """Delete the last character (DEL)."""
        if self.is_error or self.has_result:
            self.clear_all()
            return

        if not self.expression or len(self.expression) <= 1:
            self.expression = ""
            self.display_text = "0"
            self._update_display()
            return

        # If expression ends with an operator with spaces " + ", delete all 3 characters
        if self.expression.endswith(" "):
            self.expression = self.expression.rstrip()
            # Remove the trailing operator character itself
            if self.expression and self.expression[-1] in "+-×÷":
                self.expression = self.expression[:-1].rstrip()
        # If expression ends with "(-", delete both characters
        elif self.expression.endswith("(-"):
            self.expression = self.expression[:-2]
        else:
            self.expression = self.expression[:-1]

        self.display_text = self.expression if self.expression else "0"
        self._update_display()

    def clear_all(self):
        """Reset all calculator state, labels, and memory (AC)."""
        self.expression = ""
        self.display_text = "0"
        self.history_text = ""
        self.has_result = False
        self.is_error = False
        self._update_display()

    def calculate_result(self):
        """Evaluate the mathematical expression safely and display the result."""
        if self.is_error or not self.expression:
            return

        # Clean trailing operator or whitespace before evaluation
        clean_expr = self.expression.strip()
        while clean_expr and clean_expr[-1] in "+-×÷":
            clean_expr = clean_expr[:-1].strip()

        if not clean_expr:
            return

        try:
            raw_result = safe_calculate(clean_expr)
            formatted = format_result(raw_result)

            self.history_text = f"{clean_expr} ="
            self.display_text = formatted
            self.expression = formatted
            self.has_result = True
            self.is_error = False
        except ZeroDivisionError:
            self.history_text = f"{clean_expr} ="
            self.display_text = "Cannot divide by zero"
            self.is_error = True
            self.has_result = False
        except Exception:
            self.history_text = f"{clean_expr} ="
            self.display_text = "Error"
            self.is_error = True
            self.has_result = False

        self._update_display()

    # ==========================================================================
    # Physical Keyboard Handling
    # ==========================================================================

    def _bind_keyboard_events(self):
        """Bind physical keyboard and number pad keys to corresponding calculator functions."""
        self.root.bind("<Key>", self._on_key_press)

    def _on_key_press(self, event):
        """Dispatch key press events to corresponding calculator operations."""
        char = event.char
        keysym = event.keysym

        # Numbers 0 - 9
        if char in "0123456789":
            self._trigger_button(char)
            self.append_digit(char)
            return

        # Keypad numbers (KP_0 through KP_9)
        if keysym.startswith("KP_") and keysym[3:].isdigit():
            digit = keysym[3:]
            self._trigger_button(digit)
            self.append_digit(digit)
            return

        # Operators
        if char == "+":
            self._trigger_button("+")
            self.append_operator("+")
        elif char == "-":
            self._trigger_button("-")
            self.append_operator("-")
        elif char in ("*", "x", "X"):
            self._trigger_button("×")
            self.append_operator("×")
        elif char == "/":
            self._trigger_button("÷")
            self.append_operator("÷")
        elif char in (".", ","):
            self._trigger_button(".")
            self.append_decimal()

        # Calculation / Equals
        elif char == "=" or keysym in ("Return", "KP_Enter"):
            self._trigger_button("=")
            self.calculate_result()

        # Deletion
        elif keysym == "BackSpace":
            self._trigger_button("DEL")
            self.delete_char()

        # Clear All
        elif keysym == "Escape" or char.lower() == "c":
            self._trigger_button("AC")
            self.clear_all()

        # Sign toggle (F9 or 'n'/'N' key)
        elif keysym == "F9" or char.lower() == "n":
            self._trigger_button("+/-")
            self.toggle_sign()

    def _trigger_button(self, button_label: str):
        """Provide subtle visual flash feedback for keys pressed on the physical keyboard."""
        btn = self.button_widgets.get(button_label)
        if btn:
            btn.flash()


# ==============================================================================
# Application Entry Point
# ==============================================================================

def main():
    root = tk.Tk()
    Calculator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
