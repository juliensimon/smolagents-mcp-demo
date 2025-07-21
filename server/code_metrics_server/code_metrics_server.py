import ast
import json
import logging
import os
import re
import sys
from collections import Counter

# Add the project root to the path to import config_loader
sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ),
)

import gradio as gr  # noqa: E402

from config_loader import get_config_loader  # noqa: E402

# Load configuration
config_loader = get_config_loader()
server_config = config_loader.get_server_config("code_metrics")
logging_config = config_loader.get_logging_config()

# Configure logging
log_file = logging_config.get("file", "mcp_servers.log")
log_level = getattr(logging, logging_config.get("level", "INFO"))
log_format = logging_config.get(
    "format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

file_handler = logging.FileHandler(log_file)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)  # Only errors to console

logging.basicConfig(
    level=log_level,
    format=log_format,
    handlers=[file_handler, console_handler],
)
logger = logging.getLogger(__name__)


def calculate_code_complexity(code: str) -> str:
    """
    Calculate cyclomatic complexity and structural metrics for Python source code.

    This function analyzes Python source code to determine its complexity using
    cyclomatic complexity, which measures the number of linearly independent paths
    through the code. It also counts functions and classes to provide structural
    insights. The analysis uses Python's Abstract Syntax Tree (AST) for accurate
    parsing and metric calculation.

    Args:
        code (str): The Python source code to analyze. Must be valid Python syntax.
                   Can be a single function, class, module, or complete script.
                   Examples: "def hello(): return 'world'",
                            "class MyClass: pass",
                            "if x > 0: print('positive')"

    Returns:
        str: A JSON string containing complexity analysis results with the following structure:
        {
            "cyclomatic_complexity": 3,      // Integer: number of decision points + 1
            "function_count": 2,             // Integer: number of function definitions
            "class_count": 1,                // Integer: number of class definitions
            "complexity_level": "low"        // String: "low", "medium", or "high"
        }

        Complexity levels are determined as follows:
        - Low: 1-5 (simple, easy to understand)
        - Medium: 6-10 (moderate complexity)
        - High: 11+ (complex, may need refactoring)

        Cyclomatic complexity is calculated by counting:
        - Base complexity (1)
        - Each decision point (if, while, for, etc.)
        - Each exception handler
        - Each boolean operator (and, or)

    Raises:
        No exceptions are raised - all errors are returned in the JSON response.

    Examples:
        >>> code = '''
        ... def simple_function():
        ...     return "hello"
        ... '''
        >>> result = calculate_code_complexity(code)
        >>> data = json.loads(result)
        >>> print(f"Complexity: {data['cyclomatic_complexity']}")  # 1
        >>> print(f"Level: {data['complexity_level']}")  # "low"

        >>> code = '''
        ... def complex_function(x, y):
        ...     if x > 0:
        ...         if y < 0:
        ...             return "positive_x_negative_y"
        ...         else:
        ...             return "positive_x_positive_y"
        ...     else:
        ...         return "negative_x"
        ... '''
        >>> result = calculate_code_complexity(code)
        >>> data = json.loads(result)
        >>> print(f"Complexity: {data['cyclomatic_complexity']}")  # 4
        >>> print(f"Level: {data['complexity_level']}")  # "low"

    Notes:
        - Uses Python's ast module for accurate syntax parsing
        - Cyclomatic complexity is a widely-used metric for code quality
        - Higher complexity indicates more decision points and potential bugs
        - Function and class counts help assess code organization
        - Invalid Python syntax will return an error response
        - Results are logged for monitoring and debugging purposes
    """
    logger.info("Starting calculate_code_complexity function")

    # Input validation and sanitization
    if not isinstance(code, str):
        logger.error("Input is not a string")
        error_result = {
            "error": "Invalid input type",
            "details": "Input must be a string containing Python code",
        }
        return json.dumps(error_result)

    if not code.strip():
        logger.error("Empty or whitespace-only input")
        error_result = {
            "error": "Empty input",
            "details": "Input code cannot be empty or contain only whitespace",
        }
        return json.dumps(error_result)

    # Check for potentially dangerous patterns before parsing
    dangerous_patterns = [
        r"__import__\s*\(",
        r"eval\s*\(",
        r"exec\s*\(",
        r"compile\s*\(",
        r"input\s*\(",
        r"open\s*\(",
        r"file\s*\(",
        r"raw_input\s*\(",
        r"getattr\s*\(",
        r"setattr\s*\(",
        r"delattr\s*\(",
        r"hasattr\s*\(",
        r"globals\s*\(",
        r"locals\s*\(",
        r"vars\s*\(",
        r"dir\s*\(",
        r"type\s*\(",
        r"isinstance\s*\(",
        r"issubclass\s*\(",
        r"super\s*\(",
        r"property\s*\(",
        r"staticmethod\s*\(",
        r"classmethod\s*\(",
        r"abs\s*\(",
        r"all\s*\(",
        r"any\s*\(",
        r"bin\s*\(",
        r"bool\s*\(",
        r"chr\s*\(",
        r"dict\s*\(",
        r"enumerate\s*\(",
        r"filter\s*\(",
        r"float\s*\(",
        r"format\s*\(",
        r"frozenset\s*\(",
        r"hash\s*\(",
        r"hex\s*\(",
        r"int\s*\(",
        r"iter\s*\(",
        r"len\s*\(",
        r"list\s*\(",
        r"map\s*\(",
        r"max\s*\(",
        r"min\s*\(",
        r"next\s*\(",
        r"oct\s*\(",
        r"ord\s*\(",
        r"pow\s*\(",
        r"print\s*\(",
        r"range\s*\(",
        r"repr\s*\(",
        r"reversed\s*\(",
        r"round\s*\(",
        r"set\s*\(",
        r"slice\s*\(",
        r"sorted\s*\(",
        r"str\s*\(",
        r"sum\s*\(",
        r"tuple\s*\(",
        r"zip\s*\(",
    ]

    import re

    for pattern in dangerous_patterns:
        if re.search(pattern, code, re.IGNORECASE):
            logger.warning(
                f"Potentially dangerous pattern detected: {pattern}"
            )
            # Continue analysis but log the warning

    # Check for common syntax issues that might cause problems
    syntax_issues = []

    # Check for leading zeros in integer literals (Python 3 syntax error)
    leading_zero_pattern = r"\b0[0-9]+\b"
    leading_zero_matches = re.findall(leading_zero_pattern, code)
    if leading_zero_matches:
        syntax_issues.append(
            f"Leading zeros in integer literals: {leading_zero_matches}"
        )

    # Check for invalid indentation
    lines = code.split("\n")
    for i, line in enumerate(lines, 1):
        if (
            line.strip()
            and not line.startswith(" ")
            and not line.startswith("\t")
        ):
            # This line should be at the root level
            pass
        elif line.strip():
            # Check for mixed tabs and spaces
            if "\t" in line and " " in line[: len(line) - len(line.lstrip())]:
                syntax_issues.append(f"Mixed tabs and spaces at line {i}")

    logger.info(f"Input code length: {len(code)} characters")
    if syntax_issues:
        logger.warning(f"Syntax issues detected: {syntax_issues}")

    try:
        # Attempt to parse the code
        tree = ast.parse(code)
        complexity = 1  # Base complexity

        # Walk through the AST to calculate complexity
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, ast.With):
                complexity += 1
            elif isinstance(node, ast.AsyncWith):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
            elif isinstance(node, ast.Assert):
                complexity += 1
            elif isinstance(node, ast.Return):
                # Multiple return statements can indicate complexity
                pass  # Already counted in function definition
            elif isinstance(node, ast.Raise):
                complexity += 1

        # Count functions and classes
        functions = len(
            [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        )
        classes = len(
            [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        )

        # Count other structural elements
        imports = len(
            [
                n
                for n in ast.walk(tree)
                if isinstance(n, (ast.Import, ast.ImportFrom))
            ]
        )
        assignments = len(
            [n for n in ast.walk(tree) if isinstance(n, ast.Assign)]
        )
        calls = len([n for n in ast.walk(tree) if isinstance(n, ast.Call)])

        # Determine complexity level
        if complexity <= 5:
            complexity_level = "low"
        elif complexity <= 10:
            complexity_level = "medium"
        else:
            complexity_level = "high"

        result = {
            "cyclomatic_complexity": complexity,
            "function_count": functions,
            "class_count": classes,
            "import_count": imports,
            "assignment_count": assignments,
            "call_count": calls,
            "complexity_level": complexity_level,
            "warnings": syntax_issues if syntax_issues else None,
        }

        logger.info(
            f"Complexity analysis completed - Complexity: {complexity}, Functions: {functions}, Classes: {classes}"
        )
        logger.info(
            "calculate_code_complexity function completed successfully"
        )
        return json.dumps(result)

    except SyntaxError as e:
        logger.error(f"Syntax error in calculate_code_complexity: {str(e)}")
        error_result = {
            "error": "Invalid Python syntax",
            "details": str(e),
            "line": getattr(e, "lineno", "unknown"),
            "offset": getattr(e, "offset", "unknown"),
            "text": getattr(e, "text", "unknown"),
        }
        logger.info("calculate_code_complexity function completed with error")
        return json.dumps(error_result)

    except IndentationError as e:
        logger.error(
            f"Indentation error in calculate_code_complexity: {str(e)}"
        )
        error_result = {
            "error": "Indentation error",
            "details": str(e),
            "line": getattr(e, "lineno", "unknown"),
            "offset": getattr(e, "offset", "unknown"),
            "text": getattr(e, "text", "unknown"),
        }
        logger.info("calculate_code_complexity function completed with error")
        return json.dumps(error_result)

    except ValueError as e:
        logger.error(f"Value error in calculate_code_complexity: {str(e)}")
        error_result = {"error": "Value error", "details": str(e)}
        logger.info("calculate_code_complexity function completed with error")
        return json.dumps(error_result)

    except Exception as e:
        logger.error(
            f"Unexpected error in calculate_code_complexity: {str(e)}"
        )
        error_result = {
            "error": "Analysis failed",
            "details": str(e),
            "error_type": type(e).__name__,
        }
        logger.info("calculate_code_complexity function completed with error")
        return json.dumps(error_result)


def analyze_code_style(code: str) -> str:
    """
    Analyze Python code style and formatting compliance with PEP 8 guidelines.

    This function examines Python source code for common style and formatting issues
    that violate PEP 8 (Python's official style guide). It checks for line length,
    whitespace usage, indentation consistency, and other formatting standards that
    improve code readability and maintainability.

    Args:
        code (str): The Python source code to analyze for style issues. Can be any
                   valid Python code including functions, classes, modules, or scripts.
                   Examples: "def hello(): return 'world'",
                            "x=1+2",
                            "def long_function_name_with_many_parameters(...):"

    Returns:
        str: A JSON string containing style analysis results with the following structure:
        {
            "style_score": 85,                    // Integer: 0-100 style compliance score
            "issues_found": 3,                    // Integer: number of style issues
            "issues": [                           // List of style issue descriptions
                "Long lines found at: [5, 12]",
                "Trailing whitespace at lines: [8]",
                "Mixed tabs and spaces detected"
            ],
            "recommendations": [                  // List of improvement suggestions
                "Use 4 spaces for indentation",
                "Limit lines to 79 characters",
                "Remove trailing whitespace"
            ],
            "compliance_level": "good"            // String: "excellent", "good", "needs_improvement"
        }

        Compliance levels are determined as follows:
        - Excellent: 90-100 (minimal issues)
        - Good: 70-89 (some issues, generally compliant)
        - Needs Improvement: 0-69 (significant style violations)

    Raises:
        No exceptions are raised - all errors are returned in the JSON response.

    Examples:
        >>> code = '''
        ... def hello():
        ...     print("Hello, World!")
        ... '''
        >>> result = analyze_code_style(code)
        >>> data = json.loads(result)
        >>> print(f"Style score: {data['style_score']}")  # Likely 90+
        >>> print(f"Issues found: {data['issues_found']}")  # Likely 0

        >>> code = '''
        ... def bad_style():
        ...     x=1+2
        ...     print("very long line that exceeds the recommended 79 character limit")
        ... '''
        >>> result = analyze_code_style(code)
        >>> data = json.loads(result)
        >>> print(f"Style score: {data['style_score']}")  # Likely < 70
        >>> print(f"Issues: {data['issues']}")  # List of style violations

    Notes:
        - Based on PEP 8 Python style guide recommendations
        - Checks line length (79 character limit)
        - Detects trailing whitespace and mixed indentation
        - Identifies common formatting issues
        - Provides actionable recommendations for improvement
        - Style score is calculated based on number and severity of issues
        - Results are logged for monitoring and debugging purposes
    """
    logger.info("Starting analyze_code_style function")
    logger.info(f"Input code length: {len(code)} characters")

    try:
        lines = code.split("\n")
        issues = []

        # Check line length
        long_lines = [i + 1 for i, line in enumerate(lines) if len(line) > 79]
        if long_lines:
            issues.append(f"Long lines found at: {long_lines}")

        # Check for trailing whitespace
        trailing_whitespace = [
            i + 1 for i, line in enumerate(lines) if line.rstrip() != line
        ]
        if trailing_whitespace:
            issues.append(
                f"Trailing whitespace at lines: {trailing_whitespace}"
            )

        # Check for mixed tabs and spaces
        has_tabs = any("\t" in line for line in lines)
        has_spaces = any(line.startswith(" ") for line in lines)
        if has_tabs and has_spaces:
            issues.append("Mixed tabs and spaces detected")

        # Count blank lines
        blank_lines = len([line for line in lines if line.strip() == ""])
        blank_line_ratio = blank_lines / len(lines) if lines else 0

        result = {
            "total_lines": len(lines),
            "blank_lines": blank_lines,
            "blank_line_ratio": round(blank_line_ratio, 3),
            "style_issues": issues,
            "style_score": max(0, 100 - len(issues) * 10),
        }

        logger.info(
            f"Style analysis completed - Total lines: {len(lines)}, Issues: {len(issues)}, Score: {result['style_score']}"
        )
        logger.info("analyze_code_style function completed successfully")
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error in analyze_code_style: {str(e)}")
        error_result = {"error": f"Style analysis failed: {str(e)}"}
        logger.info("analyze_code_style function completed with error")
        return json.dumps(error_result)


def measure_code_coverage_metrics(code: str) -> str:
    """
    Analyze code structure for potential coverage issues.

    Args:
        code (str): The source code to analyze

    Returns:
        str: JSON string with coverage-related metrics
    """
    logger.info("Starting measure_code_coverage_metrics function")

    # Input validation and sanitization
    if not isinstance(code, str):
        logger.error("Input is not a string")
        error_result = {
            "error": "Invalid input type",
            "details": "Input must be a string containing Python code",
        }
        return json.dumps(error_result)

    if not code.strip():
        logger.error("Empty or whitespace-only input")
        error_result = {
            "error": "Empty input",
            "details": "Input code cannot be empty or contain only whitespace",
        }
        return json.dumps(error_result)

    # Check for potentially dangerous patterns before parsing
    dangerous_patterns = [
        r"__import__\s*\(",
        r"eval\s*\(",
        r"exec\s*\(",
        r"compile\s*\(",
        r"input\s*\(",
        r"open\s*\(",
        r"file\s*\(",
        r"raw_input\s*\(",
    ]

    import re

    for pattern in dangerous_patterns:
        if re.search(pattern, code, re.IGNORECASE):
            logger.warning(
                f"Potentially dangerous pattern detected: {pattern}"
            )

    # Check for common syntax issues
    syntax_issues = []

    # Check for leading zeros in integer literals
    leading_zero_pattern = r"\b0[0-9]+\b"
    leading_zero_matches = re.findall(leading_zero_pattern, code)
    if leading_zero_matches:
        syntax_issues.append(
            f"Leading zeros in integer literals: {leading_zero_matches}"
        )

    # Check for unterminated strings
    lines = code.split("\n")
    for i, line in enumerate(lines, 1):
        # Simple check for unmatched quotes
        single_quotes = line.count("'") % 2
        double_quotes = line.count('"') % 2
        if single_quotes != 0 or double_quotes != 0:
            syntax_issues.append(f"Potential unmatched quotes at line {i}")

    logger.info(f"Input code length: {len(code)} characters")
    if syntax_issues:
        logger.warning(f"Syntax issues detected: {syntax_issues}")

    try:
        # Attempt to parse the code
        tree = ast.parse(code)

        # Count different types of statements
        statements = {
            "if": 0,
            "for": 0,
            "while": 0,
            "try": 0,
            "except": 0,
            "with": 0,
            "return": 0,
            "raise": 0,
            "assert": 0,
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                statements["if"] += 1
            elif isinstance(node, ast.For):
                statements["for"] += 1
            elif isinstance(node, ast.While):
                statements["while"] += 1
            elif isinstance(node, ast.Try):
                statements["try"] += 1
            elif isinstance(node, ast.ExceptHandler):
                statements["except"] += 1
            elif isinstance(node, ast.With):
                statements["with"] += 1
            elif isinstance(node, ast.Return):
                statements["return"] += 1
            elif isinstance(node, ast.Raise):
                statements["raise"] += 1
            elif isinstance(node, ast.Assert):
                statements["assert"] += 1

        # Calculate branch complexity
        branch_complexity = (
            statements["if"] + statements["for"] + statements["while"]
        )

        # Estimate testability
        testability_score = 100
        if statements["if"] > 10:
            testability_score -= 20
        if statements["try"] > 5:
            testability_score -= 15
        if branch_complexity > 20:
            testability_score -= 25

        result = {
            "branch_complexity": branch_complexity,
            "conditional_statements": statements["if"],
            "loop_statements": statements["for"] + statements["while"],
            "exception_handling": statements["try"] + statements["except"],
            "testability_score": max(0, testability_score),
            "coverage_risk": (
                "high"
                if branch_complexity > 15
                else "medium"
                if branch_complexity > 8
                else "low"
            ),
            "warnings": syntax_issues if syntax_issues else None,
        }

        logger.info(
            f"Coverage analysis completed - Branch complexity: {branch_complexity}, Testability score: {testability_score}"
        )
        logger.info(
            "measure_code_coverage_metrics function completed successfully"
        )
        return json.dumps(result)

    except SyntaxError as e:
        logger.error(
            f"Syntax error in measure_code_coverage_metrics: {str(e)}"
        )
        error_result = {
            "error": "Invalid Python syntax",
            "details": str(e),
            "line": getattr(e, "lineno", "unknown"),
            "offset": getattr(e, "offset", "unknown"),
            "text": getattr(e, "text", "unknown"),
        }
        logger.info(
            "measure_code_coverage_metrics function completed with error"
        )
        return json.dumps(error_result)

    except IndentationError as e:
        logger.error(
            f"Indentation error in measure_code_coverage_metrics: {str(e)}"
        )
        error_result = {
            "error": "Indentation error",
            "details": str(e),
            "line": getattr(e, "lineno", "unknown"),
            "offset": getattr(e, "offset", "unknown"),
            "text": getattr(e, "text", "unknown"),
        }
        logger.info(
            "measure_code_coverage_metrics function completed with error"
        )
        return json.dumps(error_result)

    except Exception as e:
        logger.error(
            f"Unexpected error in measure_code_coverage_metrics: {str(e)}"
        )
        error_result = {
            "error": "Coverage analysis failed",
            "details": str(e),
            "error_type": type(e).__name__,
        }
        logger.info(
            "measure_code_coverage_metrics function completed with error"
        )
        return json.dumps(error_result)


def analyze_naming_conventions(code: str) -> str:
    """
    Analyze naming conventions and identifier quality.

    Args:
        code (str): The source code to analyze

    Returns:
        str: JSON string with naming metrics
    """
    logger.info("Starting analyze_naming_conventions function")

    # Input validation and sanitization
    if not isinstance(code, str):
        logger.error("Input is not a string")
        error_result = {
            "error": "Invalid input type",
            "details": "Input must be a string containing Python code",
        }
        return json.dumps(error_result)

    if not code.strip():
        logger.error("Empty or whitespace-only input")
        error_result = {
            "error": "Empty input",
            "details": "Input code cannot be empty or contain only whitespace",
        }
        return json.dumps(error_result)

    # Check for potentially dangerous patterns before parsing
    dangerous_patterns = [
        r"__import__\s*\(",
        r"eval\s*\(",
        r"exec\s*\(",
        r"compile\s*\(",
        r"input\s*\(",
        r"open\s*\(",
        r"file\s*\(",
        r"raw_input\s*\(",
    ]

    import re

    for pattern in dangerous_patterns:
        if re.search(pattern, code, re.IGNORECASE):
            logger.warning(
                f"Potentially dangerous pattern detected: {pattern}"
            )

    # Check for common syntax issues
    syntax_issues = []

    # Check for leading zeros in integer literals
    leading_zero_pattern = r"\b0[0-9]+\b"
    leading_zero_matches = re.findall(leading_zero_pattern, code)
    if leading_zero_matches:
        syntax_issues.append(
            f"Leading zeros in integer literals: {leading_zero_matches}"
        )

    # Check for unterminated strings
    lines = code.split("\n")
    for i, line in enumerate(lines, 1):
        # Simple check for unmatched quotes
        single_quotes = line.count("'") % 2
        double_quotes = line.count('"') % 2
        if single_quotes != 0 or double_quotes != 0:
            syntax_issues.append(f"Potential unmatched quotes at line {i}")

    logger.info(f"Input code length: {len(code)} characters")
    if syntax_issues:
        logger.warning(f"Syntax issues detected: {syntax_issues}")

    try:
        # Attempt to parse the code
        tree = ast.parse(code)

        # Collect all names
        names = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                names.append(node.id)
            elif isinstance(node, ast.FunctionDef):
                names.append(node.name)
            elif isinstance(node, ast.ClassDef):
                names.append(node.name)
            elif isinstance(node, ast.arg):
                names.append(node.arg)

        # Analyze naming patterns
        issues = []
        good_names = []

        for name in names:
            if len(name) < 2:
                issues.append(f"Too short name: {name}")
            elif len(name) > 30:
                issues.append(f"Too long name: {name}")
            elif re.match(r"^[a-z_][a-z0-9_]*$", name) and not name.startswith(
                "_"
            ):
                good_names.append(name)
            elif re.match(r"^[A-Z][a-zA-Z0-9]*$", name):
                good_names.append(name)  # Class names
            else:
                issues.append(f"Poor naming convention: {name}")

        # Check for common anti-patterns
        anti_patterns = ["l", "O", "I", "a", "b", "x", "y", "z"]
        for name in names:
            if name in anti_patterns and len(name) == 1:
                issues.append(f"Single letter variable: {name}")

        naming_score = max(0, 100 - len(issues) * 5)

        result = {
            "total_identifiers": len(names),
            "good_names": len(good_names),
            "naming_issues": issues,
            "naming_score": naming_score,
            "convention_compliance": (
                round(len(good_names) / len(names) * 100, 1) if names else 100
            ),
            "warnings": syntax_issues if syntax_issues else None,
        }

        logger.info(
            f"Naming analysis completed - Total identifiers: {len(names)}, Good names: {len(good_names)}, Score: {naming_score}"
        )
        logger.info(
            "analyze_naming_conventions function completed successfully"
        )
        return json.dumps(result)

    except SyntaxError as e:
        logger.error(f"Syntax error in analyze_naming_conventions: {str(e)}")
        error_result = {
            "error": "Invalid Python syntax",
            "details": str(e),
            "line": getattr(e, "lineno", "unknown"),
            "offset": getattr(e, "offset", "unknown"),
            "text": getattr(e, "text", "unknown"),
        }
        logger.info("analyze_naming_conventions function completed with error")
        return json.dumps(error_result)

    except IndentationError as e:
        logger.error(
            f"Indentation error in analyze_naming_conventions: {str(e)}"
        )
        error_result = {
            "error": "Indentation error",
            "details": str(e),
            "line": getattr(e, "lineno", "unknown"),
            "offset": getattr(e, "offset", "unknown"),
            "text": getattr(e, "text", "unknown"),
        }
        logger.info("analyze_naming_conventions function completed with error")
        return json.dumps(error_result)

    except Exception as e:
        logger.error(
            f"Unexpected error in analyze_naming_conventions: {str(e)}"
        )
        error_result = {
            "error": "Naming analysis failed",
            "details": str(e),
            "error_type": type(e).__name__,
        }
        logger.info("analyze_naming_conventions function completed with error")
        return json.dumps(error_result)


def calculate_maintainability_index(code: str) -> str:
    """
    Calculate maintainability index and related metrics.

    Args:
        code (str): The source code to analyze

    Returns:
        str: JSON string with maintainability metrics
    """
    logger.info("Starting calculate_maintainability_index function")

    # Input validation and sanitization
    if not isinstance(code, str):
        logger.error("Input is not a string")
        error_result = {
            "error": "Invalid input type",
            "details": "Input must be a string containing Python code",
        }
        return json.dumps(error_result)

    if not code.strip():
        logger.error("Empty or whitespace-only input")
        error_result = {
            "error": "Empty input",
            "details": "Input code cannot be empty or contain only whitespace",
        }
        return json.dumps(error_result)

    # Check for potentially dangerous patterns before parsing
    dangerous_patterns = [
        r"__import__\s*\(",
        r"eval\s*\(",
        r"exec\s*\(",
        r"compile\s*\(",
        r"input\s*\(",
        r"open\s*\(",
        r"file\s*\(",
        r"raw_input\s*\(",
    ]

    import re

    for pattern in dangerous_patterns:
        if re.search(pattern, code, re.IGNORECASE):
            logger.warning(
                f"Potentially dangerous pattern detected: {pattern}"
            )

    # Check for common syntax issues
    syntax_issues = []

    # Check for leading zeros in integer literals
    leading_zero_pattern = r"\b0[0-9]+\b"
    leading_zero_matches = re.findall(leading_zero_pattern, code)
    if leading_zero_matches:
        syntax_issues.append(
            f"Leading zeros in integer literals: {leading_zero_matches}"
        )

    # Check for unterminated strings
    lines = code.split("\n")
    for i, line in enumerate(lines, 1):
        # Simple check for unmatched quotes
        single_quotes = line.count("'") % 2
        double_quotes = line.count('"') % 2
        if single_quotes != 0 or double_quotes != 0:
            syntax_issues.append(f"Potential unmatched quotes at line {i}")

    logger.info(f"Input code length: {len(code)} characters")
    if syntax_issues:
        logger.warning(f"Syntax issues detected: {syntax_issues}")

    try:
        # Attempt to parse the code
        tree = ast.parse(code)
        lines = code.split("\n")

        # Count lines of code
        loc = len(lines)
        non_empty_lines = len([line for line in lines if line.strip()])

        # Count comments
        comment_lines = len(
            [line for line in lines if line.strip().startswith("#")]
        )
        comment_ratio = (
            comment_lines / non_empty_lines if non_empty_lines > 0 else 0
        )

        # Count functions and their complexity
        functions = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
        ]
        avg_function_length = (
            sum(len(node.body) for node in functions) / len(functions)
            if functions
            else 0
        )

        # Calculate Halstead metrics
        operators = []
        operands = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                operands.append(node.id)
            elif isinstance(node, ast.Constant):
                operands.append(str(node.value))
            elif isinstance(node, (ast.BinOp, ast.UnaryOp, ast.Compare)):
                operators.append(type(node).__name__)

        unique_operators = len(set(operators))
        unique_operands = len(set(operands))
        total_operators = len(operators)
        total_operands = len(operands)

        # Calculate maintainability index (simplified)
        volume = (total_operators + total_operands) * (
            unique_operators + unique_operands
        ).bit_length()
        difficulty = (
            (unique_operators / 2) * (total_operands / unique_operands)
            if unique_operands > 0
            else 0
        )

        maintainability_index = max(
            0,
            171
            - 5.2 * volume.bit_length()
            - 0.23 * difficulty
            - 16.2 * avg_function_length,
        )

        result = {
            "lines_of_code": loc,
            "non_empty_lines": non_empty_lines,
            "comment_ratio": round(comment_ratio, 3),
            "function_count": len(functions),
            "avg_function_length": round(avg_function_length, 1),
            "maintainability_index": round(maintainability_index, 1),
            "maintainability_level": (
                "excellent"
                if maintainability_index > 85
                else (
                    "good"
                    if maintainability_index > 65
                    else "fair"
                    if maintainability_index > 25
                    else "poor"
                )
            ),
            "warnings": syntax_issues if syntax_issues else None,
        }

        logger.info(
            f"Maintainability analysis completed - LOC: {loc}, Functions: {len(functions)}, Index: {maintainability_index}"
        )
        logger.info(
            "calculate_maintainability_index function completed successfully"
        )
        return json.dumps(result)

    except SyntaxError as e:
        logger.error(
            f"Syntax error in calculate_maintainability_index: {str(e)}"
        )
        error_result = {
            "error": "Invalid Python syntax",
            "details": str(e),
            "line": getattr(e, "lineno", "unknown"),
            "offset": getattr(e, "offset", "unknown"),
            "text": getattr(e, "text", "unknown"),
        }
        logger.info(
            "calculate_maintainability_index function completed with error"
        )
        return json.dumps(error_result)

    except IndentationError as e:
        logger.error(
            f"Indentation error in calculate_maintainability_index: {str(e)}"
        )
        error_result = {
            "error": "Indentation error",
            "details": str(e),
            "line": getattr(e, "lineno", "unknown"),
            "offset": getattr(e, "offset", "unknown"),
            "text": getattr(e, "text", "unknown"),
        }
        logger.info(
            "calculate_maintainability_index function completed with error"
        )
        return json.dumps(error_result)

    except Exception as e:
        logger.error(
            f"Unexpected error in calculate_maintainability_index: {str(e)}"
        )
        error_result = {
            "error": "Maintainability analysis failed",
            "details": str(e),
            "error_type": type(e).__name__,
        }
        logger.info(
            "calculate_maintainability_index function completed with error"
        )
        return json.dumps(error_result)


def analyze_security_patterns(code: str) -> str:
    """
    Analyze code for common security issues and patterns.

    Args:
        code (str): The source code to analyze

    Returns:
        str: JSON string with security metrics
    """
    logger.info("Starting analyze_security_patterns function")
    logger.info(f"Input code length: {len(code)} characters")

    try:
        security_issues = []
        security_score = 100

        # Check for dangerous patterns
        dangerous_patterns = [
            (r"eval\s*\(", "Use of eval() function"),
            (r"exec\s*\(", "Use of exec() function"),
            (r"input\s*\(", "Use of input() without validation"),
            (r"os\.system\s*\(", "Use of os.system()"),
            (r"subprocess\.call\s*\(", "Use of subprocess.call()"),
            (r"pickle\.loads\s*\(", "Use of pickle.loads()"),
            (r"__import__\s*\(", "Use of __import__()"),
            (r"globals\s*\(", "Use of globals()"),
            (r"locals\s*\(", "Use of locals()"),
        ]

        for pattern, description in dangerous_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                security_issues.append(description)
                security_score -= 15

        # Check for hardcoded secrets
        secret_patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password"),
            (r'api_key\s*=\s*["\'][^"\']+["\']', "Hardcoded API key"),
            (r'secret\s*=\s*["\'][^"\']+["\']', "Hardcoded secret"),
            (r'token\s*=\s*["\'][^"\']+["\']', "Hardcoded token"),
        ]

        for pattern, description in secret_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                security_issues.append(description)
                security_score -= 20

        # Check for SQL injection patterns
        sql_patterns = [
            (r'f".*SELECT.*{.*}', "Potential SQL injection with f-strings"),
            (r'f".*INSERT.*{.*}', "Potential SQL injection with f-strings"),
            (r'f".*UPDATE.*{.*}', "Potential SQL injection with f-strings"),
        ]

        for pattern, description in sql_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                security_issues.append(description)
                security_score -= 25

        result = {
            "security_issues": security_issues,
            "security_score": max(0, security_score),
            "security_level": (
                "excellent"
                if security_score > 85
                else (
                    "good"
                    if security_score > 70
                    else "fair"
                    if security_score > 50
                    else "poor"
                )
            ),
            "issue_count": len(security_issues),
        }

        logger.info(
            f"Security analysis completed - Issues: {len(security_issues)}, Score: {security_score}"
        )
        logger.info(
            "analyze_security_patterns function completed successfully"
        )
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error in analyze_security_patterns: {str(e)}")
        error_result = {"error": f"Security analysis failed: {str(e)}"}
        logger.info("analyze_security_patterns function completed with error")
        return json.dumps(error_result)


def calculate_performance_metrics(code: str) -> str:
    """
    Analyze code for performance-related issues and patterns.

    Args:
        code (str): The source code to analyze

    Returns:
        str: JSON string with performance metrics
    """
    logger.info("Starting calculate_performance_metrics function")
    logger.info(f"Input code length: {len(code)} characters")

    try:
        performance_issues = []
        performance_score = 100

        # Check for inefficient patterns
        inefficient_patterns = [
            (r"for.*in.*range\(len\(", "Inefficient loop with range(len())"),
            (
                r"\.append\(.*\)\s*in\s*loop",
                "Appending in loop - consider list comprehension",
            ),
            (r"list\(.*\)\s*in\s*loop", "Creating list in loop"),
            (r"dict\(.*\)\s*in\s*loop", "Creating dict in loop"),
            (r"set\(.*\)\s*in\s*loop", "Creating set in loop"),
        ]

        for pattern, description in inefficient_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                performance_issues.append(description)
                performance_score -= 10

        # Check for nested loops
        try:
            tree = ast.parse(code)
            nested_loops = 0
            for node in ast.walk(tree):
                if isinstance(node, (ast.For, ast.While)):
                    for child in ast.walk(node):
                        if (
                            isinstance(child, (ast.For, ast.While))
                            and child != node
                        ):
                            nested_loops += 1
                            break

            if nested_loops > 0:
                performance_issues.append(f"Found {nested_loops} nested loops")
                performance_score -= nested_loops * 5
        except SyntaxError:
            pass

        # Check for memory-intensive operations
        memory_patterns = [
            (r"\.copy\(\)\s*in\s*loop", "Copying objects in loop"),
            (r"deepcopy\s*in\s*loop", "Deep copying in loop"),
            (
                r"list\(.*\)\s*\+\s*list\(.*\)",
                "List concatenation - use extend()",
            ),
        ]

        for pattern, description in memory_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                performance_issues.append(description)
                performance_score -= 15

        result = {
            "performance_issues": performance_issues,
            "performance_score": max(0, performance_score),
            "performance_level": (
                "excellent"
                if performance_score > 85
                else (
                    "good"
                    if performance_score > 70
                    else "fair"
                    if performance_score > 50
                    else "poor"
                )
            ),
            "issue_count": len(performance_issues),
        }

        logger.info(
            f"Performance analysis completed - Issues: {len(performance_issues)}, Score: {performance_score}"
        )
        logger.info(
            "calculate_performance_metrics function completed successfully"
        )
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error in calculate_performance_metrics: {str(e)}")
        error_result = {"error": f"Performance analysis failed: {str(e)}"}
        logger.info(
            "calculate_performance_metrics function completed with error"
        )
        return json.dumps(error_result)


def analyze_documentation_quality(code: str) -> str:
    """
    Analyze code documentation and comments quality.

    Args:
        code (str): The source code to analyze

    Returns:
        str: JSON string with documentation metrics
    """
    logger.info("Starting analyze_documentation_quality function")
    logger.info(f"Input code length: {len(code)} characters")

    try:
        lines = code.split("\n")

        # Count different types of comments
        docstrings = []
        inline_comments = []

        in_docstring = False
        docstring_delimiter = None

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Check for docstrings
            if '"""' in stripped or "'''" in stripped:
                if not in_docstring:
                    in_docstring = True
                    docstring_delimiter = '"""' if '"""' in stripped else "'''"
                    docstrings.append(i + 1)
                elif docstring_delimiter and docstring_delimiter in stripped:
                    in_docstring = False
                    docstring_delimiter = None
            elif in_docstring:
                docstrings.append(i + 1)
            elif stripped.startswith("#"):
                inline_comments.append(i + 1)

        # Count functions and classes
        try:
            tree = ast.parse(code)
            functions = [
                node
                for node in ast.walk(tree)
                if isinstance(node, ast.FunctionDef)
            ]
            classes = [
                node
                for node in ast.walk(tree)
                if isinstance(node, ast.ClassDef)
            ]

            # Check which functions/classes have docstrings
            documented_functions = 0
            documented_classes = 0

            for func in functions:
                if ast.get_docstring(func):
                    documented_functions += 1

            for cls in classes:
                if ast.get_docstring(cls):
                    documented_classes += 1

            doc_coverage = 0.0
            if functions or classes:
                doc_coverage = (
                    (documented_functions + documented_classes)
                    / (len(functions) + len(classes))
                    * 100
                )

        except SyntaxError:
            functions = []
            classes = []
            documented_functions = 0
            documented_classes = 0
            doc_coverage = 0.0

        # Calculate documentation score
        total_lines = len(lines)
        comment_lines = len(inline_comments) + len(docstrings)
        comment_ratio = comment_lines / total_lines if total_lines > 0 else 0

        doc_score = min(100, doc_coverage + (comment_ratio * 100))

        result = {
            "total_lines": total_lines,
            "comment_lines": comment_lines,
            "comment_ratio": round(comment_ratio, 3),
            "function_count": len(functions),
            "documented_functions": documented_functions,
            "class_count": len(classes),
            "documented_classes": documented_classes,
            "documentation_coverage": round(doc_coverage, 1),
            "documentation_score": round(doc_score, 1),
            "doc_quality_level": (
                "excellent"
                if doc_score > 80
                else "good"
                if doc_score > 60
                else "fair"
                if doc_score > 40
                else "poor"
            ),
        }

        logger.info(
            f"Documentation analysis completed - Total lines: {total_lines}, Coverage: {doc_coverage}%, Score: {doc_score}"
        )
        logger.info(
            "analyze_documentation_quality function completed successfully"
        )
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error in analyze_documentation_quality: {str(e)}")
        error_result = {"error": f"Documentation analysis failed: {str(e)}"}
        logger.info(
            "analyze_documentation_quality function completed with error"
        )
        return json.dumps(error_result)


def calculate_code_duplication(code: str) -> str:
    """
    Analyze code for duplication patterns and similar code blocks.

    Args:
        code (str): The source code to analyze

    Returns:
        str: JSON string with duplication metrics
    """
    logger.info("Starting calculate_code_duplication function")
    logger.info(f"Input code length: {len(code)} characters")

    try:
        lines = code.split("\n")

        # Simple duplication detection based on line similarity
        line_frequency = Counter(lines)
        duplicate_lines = {
            line: count
            for line, count in line_frequency.items()
            if count > 1 and line.strip()
        }

        # Calculate duplication percentage
        total_lines = len(lines)
        duplicate_line_count = sum(
            count - 1 for count in duplicate_lines.values()
        )
        duplication_percentage = (
            (duplicate_line_count / total_lines * 100)
            if total_lines > 0
            else 0
        )

        # Find potential code blocks (consecutive duplicate lines)
        consecutive_duplicates = []
        min_block_size = 3

        for i in range(len(lines) - min_block_size + 1):
            block = lines[i : i + min_block_size]
            if len(set(block)) == 1 and block[0].strip():
                consecutive_duplicates.append((i + 1, i + min_block_size))

        # Calculate duplication score
        duplication_score = max(0, 100 - duplication_percentage * 2)

        result = {
            "total_lines": total_lines,
            "duplicate_lines": len(duplicate_lines),
            "duplicate_line_count": duplicate_line_count,
            "duplication_percentage": round(duplication_percentage, 2),
            "consecutive_duplicate_blocks": len(consecutive_duplicates),
            "duplication_score": round(duplication_score, 1),
            "duplication_level": (
                "excellent"
                if duplication_score > 90
                else (
                    "good"
                    if duplication_score > 75
                    else "fair"
                    if duplication_score > 50
                    else "poor"
                )
            ),
            "most_duplicated_lines": (
                list(duplicate_lines.keys())[:5] if duplicate_lines else []
            ),
        }

        logger.info(
            f"Duplication analysis completed - Total lines: {total_lines}, Duplication: {duplication_percentage}%, Score: {duplication_score}"
        )
        logger.info(
            "calculate_code_duplication function completed successfully"
        )
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error in calculate_code_duplication: {str(e)}")
        error_result = {"error": f"Duplication analysis failed: {str(e)}"}
        logger.info("calculate_code_duplication function completed with error")
        return json.dumps(error_result)


def analyze_error_handling(code: str) -> str:
    """
    Analyze error handling patterns and robustness.

    Args:
        code (str): The source code to analyze

    Returns:
        str: JSON string with error handling metrics
    """
    logger.info("Starting analyze_error_handling function")

    # Input validation and sanitization
    if not isinstance(code, str):
        logger.error("Input is not a string")
        error_result = {
            "error": "Invalid input type",
            "details": "Input must be a string containing Python code",
        }
        return json.dumps(error_result)

    if not code.strip():
        logger.error("Empty or whitespace-only input")
        error_result = {
            "error": "Empty input",
            "details": "Input code cannot be empty or contain only whitespace",
        }
        return json.dumps(error_result)

    # Check for potentially dangerous patterns before parsing
    dangerous_patterns = [
        r"__import__\s*\(",
        r"eval\s*\(",
        r"exec\s*\(",
        r"compile\s*\(",
        r"input\s*\(",
        r"open\s*\(",
        r"file\s*\(",
        r"raw_input\s*\(",
    ]

    import re

    for pattern in dangerous_patterns:
        if re.search(pattern, code, re.IGNORECASE):
            logger.warning(
                f"Potentially dangerous pattern detected: {pattern}"
            )

    # Check for common syntax issues
    syntax_issues = []

    # Check for leading zeros in integer literals
    leading_zero_pattern = r"\b0[0-9]+\b"
    leading_zero_matches = re.findall(leading_zero_pattern, code)
    if leading_zero_matches:
        syntax_issues.append(
            f"Leading zeros in integer literals: {leading_zero_matches}"
        )

    # Check for unterminated strings
    lines = code.split("\n")
    for i, line in enumerate(lines, 1):
        # Simple check for unmatched quotes
        single_quotes = line.count("'") % 2
        double_quotes = line.count('"') % 2
        if single_quotes != 0 or double_quotes != 0:
            syntax_issues.append(f"Potential unmatched quotes at line {i}")

    logger.info(f"Input code length: {len(code)} characters")
    if syntax_issues:
        logger.warning(f"Syntax issues detected: {syntax_issues}")

    try:
        # Attempt to parse the code
        tree = ast.parse(code)

        # Count different error handling constructs
        try_blocks = len(
            [node for node in ast.walk(tree) if isinstance(node, ast.Try)]
        )
        except_blocks = len(
            [
                node
                for node in ast.walk(tree)
                if isinstance(node, ast.ExceptHandler)
            ]
        )
        raise_statements = len(
            [node for node in ast.walk(tree) if isinstance(node, ast.Raise)]
        )
        assert_statements = len(
            [node for node in ast.walk(tree) if isinstance(node, ast.Assert)]
        )

        # Analyze exception handling quality
        specific_exceptions = 0
        bare_excepts = 0

        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    bare_excepts += 1
                else:
                    specific_exceptions += 1

        # Calculate error handling score
        error_handling_score = 100

        if bare_excepts > 0:
            error_handling_score -= bare_excepts * 20

        if try_blocks == 0 and raise_statements > 0:
            error_handling_score -= 30  # Raising without try-catch

        if assert_statements > 5:
            error_handling_score -= 15  # Too many assertions

        # Check for proper error handling patterns
        proper_error_handling = (
            specific_exceptions > bare_excepts if except_blocks > 0 else True
        )

        result = {
            "try_blocks": try_blocks,
            "except_blocks": except_blocks,
            "raise_statements": raise_statements,
            "assert_statements": assert_statements,
            "specific_exceptions": specific_exceptions,
            "bare_excepts": bare_excepts,
            "proper_error_handling": proper_error_handling,
            "error_handling_score": max(0, error_handling_score),
            "robustness_level": (
                "excellent"
                if error_handling_score > 85
                else (
                    "good"
                    if error_handling_score > 70
                    else "fair"
                    if error_handling_score > 50
                    else "poor"
                )
            ),
            "warnings": syntax_issues if syntax_issues else None,
        }

        logger.info(
            f"Error handling analysis completed - Try blocks: {try_blocks}, Score: {error_handling_score}"
        )
        logger.info("analyze_error_handling function completed successfully")
        return json.dumps(result)

    except SyntaxError as e:
        logger.error(f"Syntax error in analyze_error_handling: {str(e)}")
        error_result = {
            "error": "Invalid Python syntax",
            "details": str(e),
            "line": getattr(e, "lineno", "unknown"),
            "offset": getattr(e, "offset", "unknown"),
            "text": getattr(e, "text", "unknown"),
        }
        logger.info("analyze_error_handling function completed with error")
        return json.dumps(error_result)

    except IndentationError as e:
        logger.error(f"Indentation error in analyze_error_handling: {str(e)}")
        error_result = {
            "error": "Indentation error",
            "details": str(e),
            "line": getattr(e, "lineno", "unknown"),
            "offset": getattr(e, "offset", "unknown"),
            "text": getattr(e, "text", "unknown"),
        }
        logger.info("analyze_error_handling function completed with error")
        return json.dumps(error_result)

    except Exception as e:
        logger.error(f"Unexpected error in analyze_error_handling: {str(e)}")
        error_result = {
            "error": "Error handling analysis failed",
            "details": str(e),
            "error_type": type(e).__name__,
        }
        logger.info("analyze_error_handling function completed with error")
        return json.dumps(error_result)


# Create individual Gradio interfaces for each function
complexity_demo = gr.Interface(
    fn=calculate_code_complexity,
    inputs=gr.Textbox(
        placeholder="Enter Python code to analyze complexity...",
        label="Python Code",
        lines=10,
    ),
    outputs=gr.JSON(label="Complexity Analysis"),
    title="Code Complexity Analysis",
    description="Analyze cyclomatic complexity, function count, and class count of Python code.",
)

style_demo = gr.Interface(
    fn=analyze_code_style,
    inputs=gr.Textbox(
        placeholder="Enter Python code to analyze style...",
        label="Python Code",
        lines=10,
    ),
    outputs=gr.JSON(label="Style Analysis"),
    title="Code Style Analysis",
    description="Analyze code formatting, line length, whitespace, and style issues.",
)

coverage_demo = gr.Interface(
    fn=measure_code_coverage_metrics,
    inputs=gr.Textbox(
        placeholder="Enter Python code to analyze coverage...",
        label="Python Code",
        lines=10,
    ),
    outputs=gr.JSON(label="Coverage Analysis"),
    title="Code Coverage Analysis",
    description="Analyze branch complexity, testability, and coverage-related metrics.",
)

naming_demo = gr.Interface(
    fn=analyze_naming_conventions,
    inputs=gr.Textbox(
        placeholder="Enter Python code to analyze naming...",
        label="Python Code",
        lines=10,
    ),
    outputs=gr.JSON(label="Naming Analysis"),
    title="Naming Convention Analysis",
    description="Analyze identifier naming conventions and quality.",
)

maintainability_demo = gr.Interface(
    fn=calculate_maintainability_index,
    inputs=gr.Textbox(
        placeholder="Enter Python code to analyze maintainability...",
        label="Python Code",
        lines=10,
    ),
    outputs=gr.JSON(label="Maintainability Analysis"),
    title="Maintainability Analysis",
    description="Calculate maintainability index and related code quality metrics.",
)

security_demo = gr.Interface(
    fn=analyze_security_patterns,
    inputs=gr.Textbox(
        placeholder="Enter Python code to analyze security...",
        label="Python Code",
        lines=10,
    ),
    outputs=gr.JSON(label="Security Analysis"),
    title="Security Analysis",
    description="Analyze code for common security issues and dangerous patterns.",
)

performance_demo = gr.Interface(
    fn=calculate_performance_metrics,
    inputs=gr.Textbox(
        placeholder="Enter Python code to analyze performance...",
        label="Python Code",
        lines=10,
    ),
    outputs=gr.JSON(label="Performance Analysis"),
    title="Performance Analysis",
    description="Analyze code for performance issues and optimization opportunities.",
)

documentation_demo = gr.Interface(
    fn=analyze_documentation_quality,
    inputs=gr.Textbox(
        placeholder="Enter Python code to analyze documentation...",
        label="Python Code",
        lines=10,
    ),
    outputs=gr.JSON(label="Documentation Analysis"),
    title="Documentation Quality Analysis",
    description="Analyze code documentation, comments, and docstring coverage.",
)

duplication_demo = gr.Interface(
    fn=calculate_code_duplication,
    inputs=gr.Textbox(
        placeholder="Enter Python code to analyze duplication...",
        label="Python Code",
        lines=10,
    ),
    outputs=gr.JSON(label="Duplication Analysis"),
    title="Code Duplication Analysis",
    description="Analyze code for duplication patterns and similar code blocks.",
)

error_handling_demo = gr.Interface(
    fn=analyze_error_handling,
    inputs=gr.Textbox(
        placeholder="Enter Python code to analyze error handling...",
        label="Python Code",
        lines=10,
    ),
    outputs=gr.JSON(label="Error Handling Analysis"),
    title="Error Handling Analysis",
    description="Analyze error handling patterns and code robustness.",
)

# Create tabbed interface
demo = gr.TabbedInterface(
    [
        complexity_demo,
        style_demo,
        coverage_demo,
        naming_demo,
        maintainability_demo,
        security_demo,
        performance_demo,
        documentation_demo,
        duplication_demo,
        error_handling_demo,
    ],
    [
        "Complexity",
        "Style",
        "Coverage",
        "Naming",
        "Maintainability",
        "Security",
        "Performance",
        "Documentation",
        "Duplication",
        "Error Handling",
    ],
    title="Code Metrics Analysis Server",
)

# Launch the interface
if __name__ == "__main__":
    port = server_config["port"]
    logger.info(f"Starting {server_config['name']}")
    logger.info(f"Launching Gradio interface on port {port}")
    try:
        demo.launch(server_port=port, mcp_server=True)
        logger.info(f"{server_config['name']} started successfully")
    except Exception as e:
        logger.error(f"Failed to start {server_config['name']}: {str(e)}")
        raise
