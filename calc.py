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
        expression = self._strip_trailing_operators(expression)
        tokens = self._tokenize(expression)
        rpn = self._convert_to_rpn(tokens)
        return self._evaluate_rpn(rpn)

    def format_result(self, value: float) -> str:
        if abs(value) > 1e15:
            return f"{value:.2e}"
        rounded = round(value, 6)
        result = f"{rounded:.6f}".rstrip('0').rstrip('.')
        return result[:11] if len(result) > 11 else result

    def resolve_percentage(self, expression: str) -> str:
        match = re.search(r'(.+?)([+\-*/])(\d+(\.\d+)?)%$', expression)
        if not match:
            return expression
        base_expr, operator, percent_str, _ = match.groups()
        base = self.compute(base_expr)
        percent_value = base * (float(percent_str) / 100)
        return f"{base_expr}{operator}{percent_value}"

    def _strip_trailing_operators(self, expression: str) -> str:
        return expression.strip().rstrip(''.join(self.operators))

    def _tokenize(self, expression: str):
        return re.findall(r'\d+\.\d+|\d+|[()+\-*/]', expression)

    def _convert_to_rpn(self, tokens):
        precedence = {'+': 1, '-': 1, '*': 2, '/': 2}
        output = []
        operators = []
        previous_token = None

        for token in tokens:
            if re.match(r'\d+(\.\d+)?', token):
                output.append(float(token))
            elif token in precedence:
                if token == '-' and (previous_token is None or previous_token in '(-+*/'):
                    output.append(0.0)
                while operators and operators[-1] != '(' and precedence[operators[-1]] >= precedence[token]:
                    output.append(operators.pop())
                operators.append(token)
            elif token == '(':
                operators.append(token)
            elif token == ')':
                while operators and operators[-1] != '(':
                    output.append(operators.pop())
                if operators and operators[-1] == '(':
                    operators.pop()
            previous_token = token

        while operators:
            output.append(operators.pop())

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
                if token == '+':
                    stack.append(a + b)
                elif token == '-':
                    stack.append(a - b)
                elif token == '*':
                    stack.append(a * b)
                elif token == '/':
                    if b == 0:
                        raise ZeroDivisionError
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

        self.display_frame = self._create_display_frame()
        self.total_label, self.current_label = self._create_display_labels()

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
        total_label = tk.Label(self.display_frame, text=self.total_expression, anchor=tk.E,
                               bg=DARK_GRAY, fg=WHITE, padx=24, font=("Arial", 16))
        total_label.pack(expand=True, fill='both')

        current_label = tk.Label(self.display_frame, text=self.current_expression, anchor=tk.E,
                                 bg=DARK_GRAY, fg=WHITE, padx=24, font=("Arial", 40, "bold"))
        current_label.pack(expand=True, fill='both')

        return total_label, current_label

    def _create_buttons_frame(self):
        frame = tk.Frame(self.window, bg=BLACK)
        frame.pack(expand=True, fill="both")
        return frame

    def _configure_grid(self):
        for row in range(5):
            self.buttons_frame.rowconfigure(row, weight=1)
        for col in range(1, 5):
            self.buttons_frame.columnconfigure(col, weight=1)

    def _create_buttons(self):
        self._create_digit_buttons()
        self._create_operator_buttons()
        self._create_special_buttons()

    def _create_digit_buttons(self):
        for digit, position in self.digits.items():
            self._create_button(str(digit), position[0], position[1], lambda x=digit: self._add_to_expression(x))

    def _create_operator_buttons(self):
        for i, (operator, symbol) in enumerate(self.operations.items()):
            self._create_button(symbol, i, 4, lambda x=operator: self._append_operator(x))

    def _create_special_buttons(self):
        self._create_button("C", 0, 1, self._clear)
        self._create_button("x²", 0, 2, self._square)
        self._create_button("%", 0, 3, self._percentage)
        self._create_button("=", 4, 3, self.evaluate, colspan=2, bg=BLUE)

    def _create_button(self, text, row, col, command, colspan=1, bg=MEDIUM_GRAY):
        button = tk.Button(self.buttons_frame, text=text, bg=bg, fg=WHITE,
                           borderwidth=0, highlightthickness=0, relief="flat",
                           command=command, font=("Arial", 24))
        button.grid(row=row, column=col, columnspan=colspan, sticky=tk.NSEW)

    def _bind_keys(self):
        self.window.bind("<Return>", lambda event: self.evaluate())
        for key in self.digits:
            self.window.bind(str(key), lambda event, digit=key: self._add_to_expression(digit))
        for key in self.operations:
            self.window.bind(key, lambda event, operator=key: self._append_operator(operator))

    def _add_to_expression(self, value):
        if self.current_expression == "Error":
            self.current_expression = ""
        self.current_expression += str(value)
        self._update_current_label()

    def _append_operator(self, operator):
        if not self.current_expression and not self.total_expression:
            return
        self.total_expression += self.current_expression + operator
        self.current_expression = ""
        self._update_total_label()
        self._update_current_label()

    def _clear(self):
        self.current_expression = ""
        self.total_expression = ""
        self._update_total_label()
        self._update_current_label()

    def _square(self):
        try:
            value = float(self.current_expression)
            self.current_expression = self.logic.format_result(value ** 2)
        except (ValueError, TypeError):
            self.current_expression = "Error"
        self._update_current_label()

    def _percentage(self):
        if self.current_expression and not self.current_expression.endswith('%'):
            self.current_expression += '%'
            self._update_current_label()

    def evaluate(self):
        if not self.current_expression and not self.total_expression:
            return
        expression = self._prepare_expression()
        result = self._compute_expression(expression)
        self.current_expression = result
        self.total_expression = ""
        self._update_total_label()
        self._update_current_label()

    def _prepare_expression(self):
        raw = self.total_expression + self.current_expression
        return self.logic.resolve_percentage(raw.replace('×', '*').replace('÷', '/'))

    def _compute_expression(self, expression):
        try:
            result = self.logic.compute(expression)
            return self.logic.format_result(result)
        except (ZeroDivisionError, ValueError):
            return "Error"

    def _update_total_label(self):
        self.total_label.config(text=self.total_expression)

    def _update_current_label(self):
        self.current_label.config(text=self.current_expression)

if __name__ == "__main__":
    Calculator().run()
