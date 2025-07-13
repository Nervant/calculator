import tkinter as tk
import re

LARGE_FONT = ("Arial", 40, "bold")
MEDIUM_FONT = ("Arial", 30, "bold")
SMALL_FONT = ("Arial", 24, "bold")
DEFAULT_FONT = ("Arial", 20)

BLACK = "#000000"
DARK_GRAY = "#1C1C1C"
MEDIUM_GRAY = "#333333"
WHITE = "#FFFFFF"
BLUE = "#2196F3"

class CalculatorLogic:
    def __init__(self):
        self.operators = {'+', '-', '*', '/'}

    def compute(self, expression):
        expr = self._strip_trailing_operators(expression)
        tokens = self._tokenize(expr)
        rpn = self._to_rpn(tokens)
        return self._evaluate_rpn(rpn)

    def format_result(self, value):
        num = float(value)
        if abs(num) > 1e15:
            return f"{num:.2e}"
        rounded = round(num, 6)
        result = f"{rounded:.6f}".rstrip('0').rstrip('.')
        return result[:11] if len(result) > 11 else result

    def _strip_trailing_operators(self, expression):
        return expression.strip().rstrip(''.join(self.operators))

    def _tokenize(self, expression):
        return re.findall(r'\d+\.\d+|\d+|[()+\-*/]', expression)

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
                    if b == 0:
                        raise ZeroDivisionError
                    stack.append(a / b)
        if len(stack) != 1:
            raise ValueError
        return stack[0]

    def resolve_percentage(self, expression):
        match = re.search(r'(.+?)([+\-*/])(\d+(\.\d+)?)%$', expression)
        if not match:
            return expression
        base_expr, operator, percent_str, _ = match.groups()
        base = self.compute(base_expr)
        percent = float(percent_str)
        percent_value = base * (percent / 100)
        return f"{base_expr}{operator}{percent_value}"


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

        self.display_frame = self._create_display_frame()
        self.total_label, self.label = self._create_display_labels()

        self.digits = {
            7: (1, 1), 8: (1, 2), 9: (1, 3),
            4: (2, 1), 5: (2, 2), 6: (2, 3),
            1: (3, 1), 2: (3, 2), 3: (3, 3),
            0: (4, 2), '.': (4, 1)
        }

        self.operations = {"/": "÷", "*": "×", "-": "-", "+": "+"}

        self.buttons_frame = self._create_buttons_frame()
        self._configure_grid()
        self._create_buttons()
        self._bind_keys()

    def run(self):
        self.window.mainloop()

    def _create_display_frame(self):
        frame = tk.Frame(self.window, height=221, bg=DARK_GRAY)
        frame.pack(expand=True, fill="both")
        return frame

    def _create_display_labels(self):
        total_label = tk.Label(self.display_frame, text=self.total_expression, anchor=tk.E, bg=DARK_GRAY,
                               fg=WHITE, padx=24, font=SMALL_FONT)
        total_label.pack(expand=True, fill='both')

        label = tk.Label(self.display_frame, text=self.current_expression, anchor=tk.E, bg=DARK_GRAY,
                         fg=WHITE, padx=24, font=LARGE_FONT)
        label.pack(expand=True, fill='both')

        return total_label, label

    def _create_buttons_frame(self):
        frame = tk.Frame(self.window, bg=BLACK)
        frame.pack(expand=True, fill="both")
        return frame

    def _configure_grid(self):
        self.buttons_frame.rowconfigure(0, weight=1)
        for x in range(1, 5):
            self.buttons_frame.rowconfigure(x, weight=1)
            self.buttons_frame.columnconfigure(x, weight=1)

    def _create_buttons(self):
        self._create_digit_buttons()
        self._create_operator_buttons()
        self._create_clear_button()
        self._create_square_button()
        self._create_percentage_button()
        self._create_equals_button()

    def _bind_keys(self):
        self.window.bind("<Return>", lambda event: self.evaluate())
        for key in self.digits:
            self.window.bind(str(key), lambda event, digit=key: self._add_to_expression(digit))
        for key in self.operations:
            self.window.bind(key, lambda event, operator=key: self._append_operator(operator))

    def _create_digit_buttons(self):
        for digit, grid in self.digits.items():
            button = tk.Button(self.buttons_frame, text=str(digit), bg=MEDIUM_GRAY, fg=WHITE, font=SMALL_FONT,
                               borderwidth=0, highlightthickness=0, relief="flat",
                               command=lambda x=digit: self._add_to_expression(x))
            button.grid(row=grid[0], column=grid[1], sticky=tk.NSEW)

    def _create_operator_buttons(self):
        i = 0
        for operator, symbol in self.operations.items():
            button = tk.Button(self.buttons_frame, text=symbol, bg=MEDIUM_GRAY, fg=WHITE, font=DEFAULT_FONT,
                               borderwidth=0, highlightthickness=0, relief="flat",
                               command=lambda x=operator: self._append_operator(x))
            button.grid(row=i, column=4, sticky=tk.NSEW)
            i += 1

    def _create_clear_button(self):
        button = tk.Button(self.buttons_frame, text="C", bg=MEDIUM_GRAY, fg=WHITE, font=DEFAULT_FONT,
                           borderwidth=0, highlightthickness=0, relief="flat",
                           command=self._clear)
        button.grid(row=0, column=1, sticky=tk.NSEW)

    def _create_square_button(self):
        button = tk.Button(self.buttons_frame, text="x²", bg=MEDIUM_GRAY, fg=WHITE, font=DEFAULT_FONT,
                           borderwidth=0, highlightthickness=0, relief="flat",
                           command=self._square)
        button.grid(row=0, column=2, sticky=tk.NSEW)

    def _create_percentage_button(self):
        button = tk.Button(self.buttons_frame, text="%", bg=MEDIUM_GRAY, fg=WHITE, font=DEFAULT_FONT,
                           borderwidth=0, highlightthickness=0, relief="flat",
                           command=self._percentage)
        button.grid(row=0, column=3, sticky=tk.NSEW)

    def _create_equals_button(self):
        button = tk.Button(self.buttons_frame, text="=", bg=BLUE, fg=WHITE, font=DEFAULT_FONT,
                           borderwidth=0, highlightthickness=0, relief="flat",
                           command=self.evaluate)
        button.grid(row=4, column=3, columnspan=2, sticky=tk.NSEW)

    def _add_to_expression(self, value):
        if self.current_expression == "Error":
            self.current_expression = ""
        self.current_expression += str(value)
        self._update_label()

    def _append_operator(self, operator):
        if not self.current_expression and not self.total_expression:
            return
        self.total_expression += self.current_expression + self.operations[operator]
        self.current_expression = ""
        self._update_total_label()
        self._update_label()

    def _clear(self):
        self.current_expression = ""
        self.total_expression = ""
        self._update_total_label()
        self._update_label()

    def _square(self):
        try:
            value = float(self.current_expression)
            self.current_expression = self.logic.format_result(value ** 2)
        except Exception:
            self.current_expression = "Error"
        self._update_label()

    def _percentage(self):
        if self.current_expression and not self.current_expression.endswith('%'):
            self.current_expression += '%'
            self._update_label()

    def evaluate(self):
        if not self.current_expression and not self.total_expression:
            return
        expression = self.total_expression + self.current_expression
        expression = expression.replace('×', '*').replace('÷', '/')
        expression = self.logic.resolve_percentage(expression)
        try:
            result = self.logic.compute(expression)
            self.current_expression = self.logic.format_result(result)
        except Exception:
            self.current_expression = "Error"
        self.total_expression = ""
        self._update_total_label()
        self._update_label()

    def _update_total_label(self):
        self.total_label.config(text=self.total_expression)

    def _update_label(self):
        text = self.current_expression
        if len(text) <= 11:
            font = LARGE_FONT
        elif len(text) <= 18:
            font = MEDIUM_FONT
        else:
            font = SMALL_FONT
        self.label.config(text=text, font=font)


if __name__ == "__main__":
    Calculator().run()
