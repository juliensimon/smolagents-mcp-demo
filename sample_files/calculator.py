import math
import sys


class Calculator:
    def __init__(self):
        self.history = []
        self.memory = 0

    def add(self, a, b):
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result

    def subtract(self, a, b):
        result = a - b
        self.history.append(f"{a} - {b} = {result}")
        return result

    def multiply(self, a, b):
        result = a * b
        self.history.append(f"{a} * {b} = {result}")
        return result

    def divide(self, a, b):
        if b == 0:
            return "Error: Division by zero"
        result = a / b
        self.history.append(f"{a} / {b} = {result}")
        return result

    def power(self, base, exponent):
        result = base**exponent
        self.history.append(f"{base} ^ {exponent} = {result}")
        return result

    def sqrt(self, number):
        if number < 0:
            return "Error: Cannot calculate square root of negative number"
        result = math.sqrt(number)
        self.history.append(f"sqrt({number}) = {result}")
        return result

    def factorial(self, n):
        if n < 0:
            return "Error: Cannot calculate factorial of negative number"
        if n == 0:
            return 1
        result = 1
        for i in range(1, n + 1):
            result *= i
        self.history.append(f"{n}! = {result}")
        return result

    def store_in_memory(self, value):
        self.memory = value
        return f"Stored {value} in memory"

    def recall_from_memory(self):
        return self.memory

    def clear_memory(self):
        self.memory = 0
        return "Memory cleared"

    def get_history(self):
        return self.history

    def clear_history(self):
        self.history = []
        return "History cleared"


def evaluate_expression(expression):
    try:
        return eval(expression)
    except:
        return "Error: Invalid expression"


def main():
    calc = Calculator()

    print("Simple Calculator")
    print("Operations: +, -, *, /, ^, sqrt, fact, mem, hist, clear")
    print("Type 'quit' to exit")

    while True:
        try:
            user_input = input("Enter calculation: ").strip()

            if user_input.lower() == "quit":
                break
            elif user_input.lower() == "hist":
                print("History:")
                for entry in calc.get_history():
                    print(entry)
                continue
            elif user_input.lower() == "clear":
                calc.clear_history()
                print("History cleared")
                continue
            elif user_input.lower() == "mem":
                print(f"Memory value: {calc.recall_from_memory()}")
                continue

            # Parse input
            parts = user_input.split()
            if len(parts) < 2:
                print("Invalid input format")
                continue

            operation = parts[0]

            if operation == "sqrt":
                if len(parts) != 2:
                    print("Usage: sqrt <number>")
                    continue
                number = float(parts[1])
                result = calc.sqrt(number)
            elif operation == "fact":
                if len(parts) != 2:
                    print("Usage: fact <number>")
                    continue
                number = int(parts[1])
                result = calc.factorial(number)
            elif operation == "mem":
                if len(parts) != 2:
                    print("Usage: mem <number>")
                    continue
                number = float(parts[1])
                result = calc.store_in_memory(number)
            else:
                if len(parts) != 3:
                    print("Usage: <operation> <number1> <number2>")
                    continue

                a = float(parts[1])
                b = float(parts[2])

                if operation == "+":
                    result = calc.add(a, b)
                elif operation == "-":
                    result = calc.subtract(a, b)
                elif operation == "*":
                    result = calc.multiply(a, b)
                elif operation == "/":
                    result = calc.divide(a, b)
                elif operation == "^":
                    result = calc.power(a, b)
                else:
                    print("Unknown operation")
                    continue

            print(f"Result: {result}")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except:
            print("An error occurred")


if __name__ == "__main__":
    main()
