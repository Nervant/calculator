import tkinter as tk
import re

BLACK = "#000000"
DARK_GRAY = "#1C1C1C"
MEDIUM_GRAY = "#333333"
WHITE = "#FFFFFF"
BLUE = "#2196F3"

class CalculatorLogic:
    def __init__(self):
        self.operators = {'+', '-', '*', '/'}

    def compute(self, expression: str) -> float:
        expression = self._remove_trailing_operators(expression)
        tokens = self._tokenize(expression)
        rpn = self._to_rpn(tokens)
        return self._evaluate_rpn(rpn)

    def format(self, value: float) -> str:
        if abs(value) > 1e15:
            return f"{value:.2e}"
        rounded = round(value, 6)
        formatted = f"{rounded:.6f}".rstrip('0').rstrip('.')
        return formatted[:15] if len(formatted) > 15 else formatted

    def resolve_percentage(self, expression: str) -> str:
        match = re.search(r'(.+?)([+\-*/])(\d+(\.\d+)?)%$', expression)
        if not match:
            return expression
        base_expr, operator, percent_str, _ = match.groups()
        base = self.compute(base_expr)
        percent_value = base * (float(percent_str) / 100)
        return f"{base_expr}{operator}{percent_value}"

    def _remove_trailing_operators(self, expr: str) -> str:
        return expr.strip().rstrip(''.join(self.operators))

    def _tokenize(self, expr: str):
        return re.findall(r'\d+\.\d+|\d+|[()+\-*/]', expr)

    def _to_rpn(self, tokens):
        precedence = {'+': 1, '-': 1, '*': 2, '/': 2}
        output, ops = [], []
        prev = None
        for token in tokens:
            if re.match(r'\d+(\.\d+)?', token):
                output.append(float(token))
            elif token in precedence:
                if token == '-' and (prev is None or prev in '(-+*/'):
                    output.append(0.0)
                while ops and ops[-1] != '(' and precedence[ops[-1]] >= precedence[token]:
                    output.append(ops.pop())
                ops.append(token)
            elif token == '(':
                ops.append(token)
            elif token == ')':
                while ops and ops[-1] != '(':
                    output.append(ops.pop())
                if ops and ops[-1] == '(':
                    ops.pop()
            prev = token
        while ops:
            output.append(ops.pop())
        return output

    def _evaluate_rpn(self, tokens):
        stack = []
        for token in tokens:
            if isinstance(token, float):
                stack.append(token)
            else:
                if len(stack) < 2:
                    raise ValueError
                b = stack.pop()
                a = stack.pop()
                if token == '+': stack.append(a + b)
                elif token == '-': stack.append(a - b)
                elif token == '*': stack.append(a * b)
                elif token == '/':
                    if b == 0: raise ZeroDivisionError
                    stack.append(a / b)
        if len(stack) != 1:
            raise ValueError
        return stack[0]

class Calculator:
    def __init__(self):
        self.logic = CalculatorLogic()
        self.window = tk.Tk()
        self.window.geometry("375x667")
        self.window.resizable(0, 0)
        self.window.title("Calculator")
        self.window.configure(bg=BLACK)

        self.total_expression = ""
        self.current_expression = ""

        self.display_frame = self._build_display_frame()
        self.total_label, self.current_label = self._build_display_labels()

        self.digits = {
            7: (1, 1), 8: (1, 2), 9: (1, 3),
            4: (2, 1), 5: (2, 2), 6: (2, 3),
            1: (3, 1), 2: (3, 2), 3: (3, 3),
            0: (4, 2), '.': (4, 1)
        }

        self.operators = {"/": "÷", "*": "×", "-": "-", "+": "+"}
        self.inverse_operators = {v: k for k, v in self.operators.items()}

        self.buttons_frame = self._build_buttons_frame()
        self._configure_grid()
        self._add_buttons()
        self._bind_keys()

    def run(self):
        self.window.mainloop()

    def _build_display_frame(self):
        frame = tk.Frame(self.window, height=221, bg=DARK_GRAY)
        frame.pack(expand=True, fill="both")
        return frame

    def _build_display_labels(self):
        total = tk.Label(self.display_frame, anchor=tk.E, bg=DARK_GRAY, fg=WHITE, padx=24, font=("Arial", 16))
        total.pack(expand=True, fill='both')
        current = tk.Label(self.display_frame, anchor=tk.E, bg=DARK_GRAY, fg=WHITE, padx=24, font=("Arial", 40, "bold"))
        current.pack(expand=True, fill='both')
        return total, current

    def _build_buttons_frame(self):
        frame = tk.Frame(self.window, bg=BLACK)
        frame.pack(expand=True, fill="both")
        return frame

    def _configure_grid(self):
        for row in range(5):
            self.buttons_frame.rowconfigure(row, weight=1)
        for col in range(1, 5):
            self.buttons_frame.columnconfigure(col, weight=1)

    def _add_buttons(self):
        for digit, pos in self.digits.items():
            self._add_button(str(digit), pos[0], pos[1], lambda x=digit: self._append_digit(x))
        for i, (op, symbol) in enumerate(self.operators.items()):
            self._add_button(symbol, i, 4, lambda x=op: self._append_operator(x))
        self._add_button("C", 0, 1, self._clear)
        self._add_button("x²", 0, 2, self._square)
        self._add_button("%", 0, 3, self._append_percent)
        self._add_button("=", 4, 3, self._evaluate, colspan=2, bg=BLUE)

    def _add_button(self, text, row, col, command, colspan=1, bg=MEDIUM_GRAY):
        button = self._button_factory(text, command, bg)
        button.grid(row=row, column=col, columnspan=colspan, sticky=tk.NSEW)

    def _button_factory(self, text, command, bg):
        return tk.Button(
            self.buttons_frame,
            text=text,
            command=command,
            bg=bg,
            fg=WHITE,
            font=("Arial", 24),
            borderwidth=0,
            highlightthickness=0,
            highlightbackground=bg,
            highlightcolor=bg,
            relief="flat",
            activebackground=bg,
            activeforeground=WHITE,
            takefocus=0
        )

    def _bind_keys(self):
        self.window.bind("<Return>", lambda e: self._evaluate())
        for key in self.digits:
            self.window.bind(str(key), lambda e, k=key: self._append_digit(k))
        for op in self.operators:
            self.window.bind(op, lambda e, o=op: self._append_operator(o))

    def _append_digit(self, value):
        if self.current_expression == "Error":
            self.current_expression = ""
        if len(re.sub(r'\D', '', self.current_expression)) >= 15:
            return
        self.current_expression += str(value)
        self._refresh_current_label()

    def _append_operator(self, op):
        if not self.current_expression and not self.total_expression:
            return
        self.total_expression += self.current_expression + self.operators[op]
        self.current_expression = ""
        self._refresh_total_label()
        self._refresh_current_label()

    def _clear(self):
        self.current_expression = ""
        self.total_expression = ""
        self._refresh_total_label()
        self._refresh_current_label()

    def _square(self):
        try:
            value = float(self.current_expression)
            self.current_expression = self.logic.format(value ** 2)
        except:
            self.current_expression = "Error"
        self._refresh_current_label()

    def _append_percent(self):
        if self.current_expression and not self.current_expression.endswith('%'):
            self.current_expression += '%'
            self._refresh_current_label()

    def _evaluate(self):
        if not self.current_expression and not self.total_expression:
            return
        expression = self._build_expression()
        result = self._safe_compute(expression)
        self.current_expression = result
        self.total_expression = ""
        self._refresh_total_label()
        self._refresh_current_label()

    def _build_expression(self):
        raw = self.total_expression + self.current_expression
        translated = ''.join(self.inverse_operators.get(ch, ch) for ch in raw)
        return self.logic.resolve_percentage(translated)

    def _safe_compute(self, expr):
        try:
            return self.logic.format(self.logic.compute(expr))
        except:
            return "Error"

    def _adjust_font(self, text, label, max_size=40, min_size=12):
        if not text:
            return max_size
        label.update_idletasks()
        width = label.winfo_width() - 48
        size = max_size
        while size >= min_size:
            font = ("Arial", size, "bold")
            text_width = label.tk.call("font", "measure", font, text)
            if text_width <= width:
                return size
            size -= 2
        return min_size

    def _refresh_total_label(self):
        self.total_label.config(text=self.total_expression)
        if self.total_expression:
            size = self._adjust_font(self.total_expression, self.total_label, 16, 10)
            self.total_label.config(font=("Arial", size))

    def _refresh_current_label(self):
        self.current_label.config(text=self.current_expression)
        if self.current_expression:
            size = self._adjust_font(self.current_expression, self.current_label, 40, 16)
            self.current_label.config(font=("Arial", size, "bold"))

if __name__ == "__main__":
    Calculator().run()
