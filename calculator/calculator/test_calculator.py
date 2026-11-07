import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from main import safe_calculate, format_result, Calculator
import tkinter as tk

class TestCalculatorCore(unittest.TestCase):
    def test_addition(self):
        self.assertEqual(safe_calculate("15 + 27"), 42)
        self.assertEqual(safe_calculate("0.5 + 0.25"), 0.75)

    def test_subtraction(self):
        self.assertEqual(safe_calculate("100 - 35"), 65)
        self.assertEqual(safe_calculate("5.5 - 2.2"), 3.3)

    def test_multiplication(self):
        self.assertEqual(safe_calculate("8 × 9"), 72)
        self.assertEqual(safe_calculate("2.5 × 4"), 10)

    def test_division(self):
        self.assertEqual(safe_calculate("84 ÷ 4"), 21)
        self.assertEqual(safe_calculate("10 ÷ 4"), 2.5)

    def test_operator_precedence(self):
        # Multiplication before addition: 2 + (3 * 4) = 14
        self.assertEqual(safe_calculate("2 + 3 × 4"), 14)
        # Parentheses support
        self.assertEqual(safe_calculate("(2 + 3) × 4"), 20)

    def test_negative_numbers(self):
        self.assertEqual(safe_calculate("-10 + 4"), -6)
        self.assertEqual(safe_calculate("15 + (-5)"), 10)
        self.assertEqual(safe_calculate("10 × (-3)"), -30)
        self.assertEqual(safe_calculate("-4 × -5"), 20)

    def test_division_by_zero(self):
        with self.assertRaises(ZeroDivisionError):
            safe_calculate("10 ÷ 0")
        with self.assertRaises(ZeroDivisionError):
            safe_calculate("5 ÷ (2 - 2)")

    def test_format_result(self):
        self.assertEqual(format_result(42.0), "42")
        self.assertEqual(format_result(0.30000000000000004), "0.3")
        self.assertEqual(format_result(2.5), "2.5")
        self.assertEqual(format_result(0.0), "0")
        self.assertEqual(format_result(-5.0), "-5")

    def test_unsafe_eval_blocked(self):
        with self.assertRaises(Exception):
            safe_calculate("__import__('os').system('calc')")
        with self.assertRaises(Exception):
            safe_calculate("open('secret.txt')")
        with self.assertRaises(Exception):
            safe_calculate("eval('2+2')")

class TestCalculatorUIState(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.calc = Calculator(self.root)

    def tearDown(self):
        self.root.destroy()

    def test_initial_state(self):
        self.assertEqual(self.calc.display_text, "0")
        self.assertEqual(self.calc.history_text, "")
        self.assertFalse(self.calc.is_error)

    def test_number_entry(self):
        self.calc.append_digit("1")
        self.calc.append_digit("2")
        self.calc.append_digit("3")
        self.assertEqual(self.calc.display_text, "123")

    def test_decimal_prevent_duplicate(self):
        self.calc.append_digit("3")
        self.calc.append_decimal()
        self.calc.append_digit("1")
        self.calc.append_decimal()  # Second decimal should be ignored
        self.calc.append_digit("4")
        self.assertEqual(self.calc.display_text, "3.14")

    def test_operator_replacement(self):
        self.calc.append_digit("5")
        self.calc.append_operator("+")
        self.assertEqual(self.calc.display_text, "5 + ")
        self.calc.append_operator("×")  # Should replace + with ×
        self.assertEqual(self.calc.display_text, "5 × ")
        self.calc.append_digit("4")
        self.assertEqual(self.calc.display_text, "5 × 4")
        self.calc.calculate_result()
        self.assertEqual(self.calc.display_text, "20")
        self.assertEqual(self.calc.history_text, "5 × 4 =")

    def test_division_by_zero_ui(self):
        self.calc.append_digit("8")
        self.calc.append_operator("÷")
        self.calc.append_digit("0")
        self.calc.calculate_result()
        self.assertEqual(self.calc.display_text, "Cannot divide by zero")
        self.assertTrue(self.calc.is_error)

    def test_toggle_sign(self):
        self.calc.append_digit("9")
        self.calc.toggle_sign()
        self.assertEqual(self.calc.display_text, "-9")
        self.calc.toggle_sign()
        self.assertEqual(self.calc.display_text, "9")

    def test_delete_char(self):
        self.calc.append_digit("1")
        self.calc.append_digit("2")
        self.calc.append_digit("3")
        self.calc.delete_char()
        self.assertEqual(self.calc.display_text, "12")

    def test_clear_all(self):
        self.calc.append_digit("7")
        self.calc.append_operator("+")
        self.calc.append_digit("8")
        self.calc.clear_all()
        self.assertEqual(self.calc.display_text, "0")
        self.assertEqual(self.calc.history_text, "")
        self.assertEqual(self.calc.expression, "")

    def test_toggle_sign_in_expression(self):
        self.calc.append_digit("1")
        self.calc.append_digit("0")
        self.calc.append_operator("+")
        self.calc.append_digit("5")
        self.assertEqual(self.calc.display_text, "10 + 5")
        self.calc.toggle_sign()
        self.assertEqual(self.calc.display_text, "10 + (-5)")
        self.calc.calculate_result()
        self.assertEqual(self.calc.display_text, "5")
        self.assertEqual(self.calc.history_text, "10 + (-5) =")

if __name__ == "__main__":
    unittest.main()

