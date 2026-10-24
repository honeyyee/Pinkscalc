"""A playful pink bubble-style desktop calculator built with Tkinter."""

from __future__ import annotations

import ast
import operator
import tkinter as tk
from tkinter import font as tkfont


BG = "#fff0f6"
PINK = "#f7a8c4"
DEEP_PINK = "#dc6c9b"
TEXT = "#693b52"
MUTED = "#b77b96"


class BubbleButton(tk.Canvas):
    """A clickable, circular calculator key drawn on a canvas."""

    def __init__(self, master: tk.Widget, label: str, command, color: str, **kwargs):
        super().__init__(master, width=76, height=76, bg=BG, highlightthickness=0, **kwargs)
        self.label = label
        self.command = command
        self.color = color
        self.hover_color = self._mix(color, "#ffffff", 0.25)
        self.pressed_color = self._mix(color, "#b94e7d", 0.10)
        self._shape = self.create_oval(5, 5, 71, 71, fill=color, outline="")
        self._text = self.create_text(38, 38, text=label, fill=TEXT, font=("Segoe UI", 19, "bold"))
        self.bind("<Enter>", lambda _event: self.itemconfigure(self._shape, fill=self.hover_color))
        self.bind("<Leave>", lambda _event: self.itemconfigure(self._shape, fill=self.color))
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", lambda _event: self.itemconfigure(self._shape, fill=self.hover_color))
        self.configure(cursor="hand2")

    @staticmethod
    def _mix(first: str, second: str, amount: float) -> str:
        a = tuple(int(first[index:index + 2], 16) for index in (1, 3, 5))
        b = tuple(int(second[index:index + 2], 16) for index in (1, 3, 5))
        return "#" + "".join(f"{round(x + (y - x) * amount):02x}" for x, y in zip(a, b))

    def _on_press(self, _event=None) -> None:
        self.itemconfigure(self._shape, fill=self.pressed_color)
        self.command(self.label)


class Calculator:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.expression = ""
        self.just_calculated = False
        root.title("pinkscalc")
        root.configure(bg=BG)
        root.resizable(False, False)
        root.geometry("390x700")

        self._make_background()
        container = tk.Frame(root, bg=BG)
        container.pack(fill="both", expand=True, padx=24, pady=20)

        header = tk.Frame(container, bg=BG)
        header.pack(fill="x", pady=(4, 18))
        tk.Label(header, text="✿", bg=BG, fg=DEEP_PINK, font=("Segoe UI", 22)).pack(side="left")
        title = tk.Frame(header, bg=BG)
        title.pack(side="left", padx=8)
        tk.Label(title, text="pinkscalc", bg=BG, fg=TEXT, font=("Segoe UI", 18, "bold")).pack(anchor="w")
        tk.Label(title, text="a little joy in every sum", bg=BG, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w")
        tk.Label(header, text="●  ●  ●", bg=BG, fg="#f3a6c3", font=("Segoe UI", 9)).pack(side="right", padx=5)

        display = tk.Frame(container, bg="#fff9fc", highlightbackground="#f8d4e2", highlightthickness=1)
        display.pack(fill="x", pady=(0, 22), ipady=15)
        self.expression_label = tk.Label(display, text="ready when you are", anchor="e", bg="#fff9fc", fg=MUTED,
                                         font=("Segoe UI", 11), padx=18)
        self.expression_label.pack(fill="x", pady=(5, 4))
        self.display_label = tk.Label(display, text="0", anchor="e", bg="#fff9fc", fg=TEXT,
                                      font=("Segoe UI", 34, "bold"), padx=18)
        self.display_label.pack(fill="x", pady=(0, 4))

        keys_frame = tk.Frame(container, bg=BG)
        keys_frame.pack()
        rows = [
            [("AC", "#f8c9da"), ("⌫", "#f8c9da"), ("%", "#f8c9da"), ("÷", "#f4b4ce")],
            [("7", "#ffffff"), ("8", "#ffffff"), ("9", "#ffffff"), ("×", "#f4b4ce")],
            [("4", "#ffffff"), ("5", "#ffffff"), ("6", "#ffffff"), ("−", "#f4b4ce")],
            [("1", "#ffffff"), ("2", "#ffffff"), ("3", "#ffffff"), ("+", "#f4b4ce")],
            [("±", "#f8c9da"), ("0", "#ffffff"), (".", "#ffffff"), ("=", DEEP_PINK)],
        ]
        for row_index, row in enumerate(rows):
            for column_index, (label, color) in enumerate(row):
                button = BubbleButton(keys_frame, label, self.press, color)
                button.grid(row=row_index, column=column_index, padx=3, pady=4)
                if label == "=":
                    button.itemconfigure(button._text, fill="white", font=("Segoe UI", 22, "bold"))
                elif label in {"AC", "⌫", "%", "±"}:
                    button.itemconfigure(button._text, font=("Segoe UI", 15, "bold"))

        tk.Label(container, text="made with ♡", bg=BG, fg="#c98aa5", font=("Segoe UI", 9)).pack(pady=(12, 0))
        root.bind("<Key>", self.on_key)
        root.bind("<Return>", lambda _event: self.press("="))
        root.bind("<BackSpace>", lambda _event: self.press("⌫"))
        root.bind("<Escape>", lambda _event: self.press("AC"))

    def _make_background(self) -> None:
        # Subtle decorative bubbles behind the calculator.
        canvas = tk.Canvas(self.root, width=390, height=700, bg=BG, highlightthickness=0)
        canvas.place(x=0, y=0)
        canvas.create_oval(-65, 535, 85, 685, fill="#fde0eb", outline="")
        canvas.create_oval(315, 35, 430, 150, fill="#fce0eb", outline="")
        canvas.create_oval(335, 555, 395, 615, fill="#fbd2e1", outline="")

    def press(self, key: str) -> None:
        if key == "AC":
            self.expression = ""
            self.just_calculated = False
        elif key == "⌫":
            self.expression = self.expression[:-1]
            self.just_calculated = False
        elif key == "±":
            self._toggle_sign()
        elif key == "%":
            self._percent()
        elif key == "=":
            self._calculate()
            return
        elif key in "0123456789.":
            if self.just_calculated:
                self.expression = ""
                self.just_calculated = False
            if key == ".":
                current = self.expression.split(" ")[-1]
                if "." in current:
                    return
                if not current or current in {"+", "−", "×", "÷"}:
                    self.expression += "0"
            self.expression += key
        elif key in {"+", "−", "×", "÷"}:
            if not self.expression:
                if key == "−":
                    self.expression = "−"
            elif self.expression[-1] in "+−×÷":
                self.expression = self.expression[:-1] + key
            else:
                self.expression += key
            self.just_calculated = False
        self._update_display()

    def _toggle_sign(self) -> None:
        if not self.expression:
            self.expression = "−"
            return
        start = max(self.expression.rfind(operator) for operator in "+−×÷")
        number = self.expression[start + 1:]
        if number.startswith("−"):
            self.expression = self.expression[:start + 1] + number[1:]
        elif number:
            self.expression = self.expression[:start + 1] + "−" + number

    def _percent(self) -> None:
        if not self.expression or self.expression[-1] in "+−×÷":
            return
        start = max(self.expression.rfind(operator) for operator in "+−×÷")
        try:
            value = float(self.expression[start + 1:]) / 100
        except ValueError:
            return
        self.expression = self.expression[:start + 1] + self._format(value)
        self._update_display()

    def _calculate(self) -> None:
        if not self.expression:
            return
        try:
            result = self._safe_eval(self.expression)
            self.expression = self._format(result)
            self.just_calculated = True
            self.expression_label.configure(text="your answer")
            self.display_label.configure(text=self.expression)
        except (ValueError, ZeroDivisionError, OverflowError, SyntaxError):
            self.expression_label.configure(text="oops, try that again")
            self.display_label.configure(text="Error")
            self.expression = ""
            self.just_calculated = True

    @staticmethod
    def _safe_eval(expression: str) -> float:
        normalized = expression.replace("×", "*").replace("÷", "/").replace("−", "-")
        tree = ast.parse(normalized, mode="eval")
        binary_ops = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv}
        unary_ops = {ast.UAdd: operator.pos, ast.USub: operator.neg}

        def evaluate(node):
            if isinstance(node, ast.Expression):
                return evaluate(node.body)
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                return node.value
            if isinstance(node, ast.BinOp) and type(node.op) in binary_ops:
                return binary_ops[type(node.op)](evaluate(node.left), evaluate(node.right))
            if isinstance(node, ast.UnaryOp) and type(node.op) in unary_ops:
                return unary_ops[type(node.op)](evaluate(node.operand))
            raise ValueError("Unsupported expression")

        return evaluate(tree)

    @staticmethod
    def _format(value: float) -> str:
        value = float(value)
        if value == 0:
            return "0"
        if value.is_integer():
            return str(int(value))
        return f"{value:.10g}"

    def _update_display(self) -> None:
        self.expression_label.configure(text="your calculation" if self.expression else "ready when you are")
        self.display_label.configure(text=self.expression or "0")

    def on_key(self, event) -> None:
        if event.char in "0123456789.":
            self.press(event.char)
        elif event.char in "+-*/":
            self.press({"-": "−", "*": "×", "/": "÷"}.get(event.char, event.char))


def main() -> None:
    root = tk.Tk()
    Calculator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
