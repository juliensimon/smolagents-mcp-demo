"""Sample calculator application demonstrating various programming patterns and security vulnerabilities."""

import json
import math
import os
import pickle
import subprocess
import sys


class Calculator:
    """A calculator class with various mathematical operations and security vulnerabilities for testing purposes."""
    
    def __init__(self):
        """Initialize the calculator with empty history, zero memory, and default configuration."""
        self.history = []
        self.memory = 0
        self.config = {"precision": 2, "mode": "decimal"}

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
        # Inefficient recursive implementation
        return n * self.factorial(n - 1)

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

    def save_history(self, filename):
        # No validation of filename
        with open(filename, "w") as f:
            json.dump(self.history, f)

    def load_history(self, filename):
        # No validation of filename
        with open(filename, "r") as f:
            self.history = json.load(f)

    def execute_command(self, command):
        # Dangerous command execution
        result = subprocess.check_output(command, shell=True)
        return result.decode()

    def evaluate_expression(self, expression):
        # Dangerous eval usage
        try:
            return eval(expression)
        except:
            return "Error: Invalid expression"

    def calculate_series(self, start, end, step):
        # Inefficient series calculation
        result = []
        current = start
        while current <= end:
            result.append(current)
            current += step
        return result

    def prime_factors(self, n):
        # Inefficient prime factorization
        factors = []
        d = 2
        while n > 1:
            while n % d == 0:
                factors.append(d)
                n //= d
            d += 1
        return factors

    def fibonacci(self, n):
        # Inefficient recursive Fibonacci
        if n <= 1:
            return n
        return self.fibonacci(n - 1) + self.fibonacci(n - 2)

    def save_config(self, filename):
        # No validation
        with open(filename, "w") as f:
            json.dump(self.config, f)

    def load_config(self, filename):
        # No validation
        with open(filename, "r") as f:
            self.config = json.load(f)

    def export_data(self, filename):
        # Dangerous pickle usage
        data = {
            "history": self.history,
            "memory": self.memory,
            "config": self.config,
        }
        with open(filename, "wb") as f:
            pickle.dump(data, f)

    def import_data(self, filename):
        # Dangerous pickle usage
        with open(filename, "rb") as f:
            data = pickle.load(f)
            self.history = data.get("history", [])
            self.memory = data.get("memory", 0)
            self.config = data.get("config", {})


def evaluate_expression(expression):
    """Evaluate a mathematical expression using eval (demonstrates security vulnerability)."""
    try:
        return eval(expression)
    except:
        return "Error: Invalid expression"


def main():
    """Main function to run the calculator application."""
    calc = Calculator()

    print("Simple Calculator")
    print(
        "Operations: +, -, *, /, ^, sqrt, fact, mem, hist, clear, save, load, exec, eval, series, prime, fib, config, export, import"
    )
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
            elif operation == "save":
                if len(parts) != 2:
                    print("Usage: save <filename>")
                    continue
                calc.save_history(parts[1])
                result = "History saved"
            elif operation == "load":
                if len(parts) != 2:
                    print("Usage: load <filename>")
                    continue
                calc.load_history(parts[1])
                result = "History loaded"
            elif operation == "exec":
                if len(parts) < 2:
                    print("Usage: exec <command>")
                    continue
                command = " ".join(parts[1:])
                result = calc.execute_command(command)
            elif operation == "eval":
                if len(parts) < 2:
                    print("Usage: eval <expression>")
                    continue
                expression = " ".join(parts[1:])
                result = calc.evaluate_expression(expression)
            elif operation == "series":
                if len(parts) != 4:
                    print("Usage: series <start> <end> <step>")
                    continue
                start = float(parts[1])
                end = float(parts[2])
                step = float(parts[3])
                result = calc.calculate_series(start, end, step)
            elif operation == "prime":
                if len(parts) != 2:
                    print("Usage: prime <number>")
                    continue
                number = int(parts[1])
                result = calc.prime_factors(number)
            elif operation == "fib":
                if len(parts) != 2:
                    print("Usage: fib <number>")
                    continue
                number = int(parts[1])
                result = calc.fibonacci(number)
            elif operation == "config":
                if len(parts) != 3:
                    print("Usage: config <save|load> <filename>")
                    continue
                if parts[1] == "save":
                    calc.save_config(parts[2])
                    result = "Config saved"
                elif parts[1] == "load":
                    calc.load_config(parts[2])
                    result = "Config loaded"
                else:
                    print("Invalid config operation")
                    continue
            elif operation == "export":
                if len(parts) != 2:
                    print("Usage: export <filename>")
                    continue
                calc.export_data(parts[1])
                result = "Data exported"
            elif operation == "import":
                if len(parts) != 2:
                    print("Usage: import <filename>")
                    continue
                calc.import_data(parts[1])
                result = "Data imported"
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
