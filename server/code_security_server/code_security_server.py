import json
import logging
import os
import re
import sys
from typing import Any, Dict, List

# Add the project root to the path to import config_loader
sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ),
)

import gradio as gr

from config_loader import get_config_loader

# Load configuration
config_loader = get_config_loader()
server_config = config_loader.get_server_config("code_security")
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


def analyze_sql_injection(code: str) -> str:
    """
    Analyze Python source code for SQL injection vulnerabilities and security risks.

    This function performs static code analysis to detect potential SQL injection
    vulnerabilities in Python code. It scans for common patterns that could lead
    to SQL injection attacks, such as dynamic SQL query construction with user input,
    string concatenation in SQL statements, and unsafe formatting methods. The analysis
    helps identify security weaknesses before they can be exploited.

    Args:
        code (str): The Python source code to analyze for SQL injection vulnerabilities.
                   Can be a single function, class, module, or complete script.
                   Examples: "query = f'SELECT * FROM users WHERE id = {user_id}'",
                            "sql = 'SELECT * FROM users WHERE name = ' + user_input",
                            "cursor.execute('SELECT * FROM users WHERE id = %s' % user_id)"

    Returns:
        str: A JSON string containing SQL injection analysis results with the following structure:
        {
            "vulnerabilities": [                    // List of detected vulnerabilities
                {
                    "type": "SQL Injection",       // String: vulnerability type
                    "description": "F-string SQL query with variable interpolation", // String: detailed description
                    "line": 15,                    // Integer: line number where vulnerability was found
                    "code": "f'SELECT * FROM users WHERE id = {user_id}'", // String: vulnerable code snippet
                    "severity": "high"             // String: "high", "medium", or "low"
                }
            ],
            "risk_level": "high",                  // String: overall risk assessment
            "vulnerability_count": 3,              // Integer: total number of vulnerabilities found
            "recommendations": [                   // List of security improvement suggestions
                "Use parameterized queries with placeholders",
                "Use ORM libraries like SQLAlchemy",
                "Validate and sanitize all user inputs",
                "Use database connection libraries with built-in protection"
            ]
        }

        Risk levels are determined as follows:
        - Low: 0 vulnerabilities found
        - Medium: 1-3 vulnerabilities found
        - High: 4+ vulnerabilities found

    Raises:
        No exceptions are raised - all errors are returned in the JSON response.

    Examples:
        >>> code = '''
        ... def get_user(user_id):
        ...     query = f"SELECT * FROM users WHERE id = {user_id}"
        ...     return execute_query(query)
        ... '''
        >>> result = analyze_sql_injection(code)
        >>> data = json.loads(result)
        >>> print(f"Risk level: {data['risk_level']}")  # "high"
        >>> print(f"Vulnerabilities found: {data['vulnerability_count']}")  # 1
        >>> for vuln in data['vulnerabilities']:
        ...     print(f"Line {vuln['line']}: {vuln['description']}")

        >>> code = '''
        ... def get_user(user_id):
        ...     query = "SELECT * FROM users WHERE id = %s"
        ...     return execute_query(query, (user_id,))
        ... '''
        >>> result = analyze_sql_injection(code)
        >>> data = json.loads(result)
        >>> print(f"Risk level: {data['risk_level']}")  # "low"

    Notes:
        - Detects multiple SQL injection patterns including f-strings, string concatenation, and formatting
        - Covers common SQL operations: SELECT, INSERT, UPDATE, DELETE, DROP, CREATE
        - Provides line numbers for easy vulnerability location
        - Includes severity assessment for each vulnerability
        - Offers actionable security recommendations
        - Uses regex patterns for pattern matching (case-insensitive)
        - Results are logged for monitoring and debugging purposes
        - This is static analysis - runtime behavior may differ
    """
    logger.info("Starting analyze_sql_injection function")
    logger.info(f"Input code length: {len(code)} characters")

    sql_injection_patterns = [
        # F-string SQL queries
        (
            r'f".*SELECT.*{.*}',
            "F-string SQL query with variable interpolation",
        ),
        (
            r'f".*INSERT.*{.*}',
            "F-string SQL INSERT with variable interpolation",
        ),
        (
            r'f".*UPDATE.*{.*}',
            "F-string SQL UPDATE with variable interpolation",
        ),
        (
            r'f".*DELETE.*{.*}',
            "F-string SQL DELETE with variable interpolation",
        ),
        (r'f".*DROP.*{.*}', "F-string SQL DROP with variable interpolation"),
        (
            r'f".*CREATE.*{.*}',
            "F-string SQL CREATE with variable interpolation",
        ),
        # String concatenation SQL
        (r'["\']\s*SELECT.*\s*\+\s*', "SQL query with string concatenation"),
        (r'["\']\s*INSERT.*\s*\+\s*', "SQL INSERT with string concatenation"),
        (r'["\']\s*UPDATE.*\s*\+\s*', "SQL UPDATE with string concatenation"),
        (r'["\']\s*DELETE.*\s*\+\s*', "SQL DELETE with string concatenation"),
        # Format string SQL
        (r'["\']\s*SELECT.*\s*\.format\(', "SQL query with .format() method"),
        (r'["\']\s*INSERT.*\s*\.format\(', "SQL INSERT with .format() method"),
        (r'["\']\s*UPDATE.*\s*\.format\(', "SQL UPDATE with .format() method"),
        # % formatting SQL
        (r'["\']\s*SELECT.*\s*%\s*', "SQL query with % formatting"),
        (r'["\']\s*INSERT.*\s*%\s*', "SQL INSERT with % formatting"),
        (r'["\']\s*UPDATE.*\s*%\s*', "SQL UPDATE with % formatting"),
    ]

    vulnerabilities = []
    risk_level = "low"

    for pattern, description in sql_injection_patterns:
        matches = re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            line_num = code[: match.start()].count("\n") + 1
            vulnerabilities.append(
                {
                    "type": "SQL Injection",
                    "description": description,
                    "line": line_num,
                    "code": (
                        match.group(0)[:100] + "..."
                        if len(match.group(0)) > 100
                        else match.group(0)
                    ),
                    "severity": "high",
                }
            )

    if vulnerabilities:
        risk_level = "high" if len(vulnerabilities) > 3 else "medium"

    result = {
        "vulnerabilities": vulnerabilities,
        "risk_level": risk_level,
        "vulnerability_count": len(vulnerabilities),
        "recommendations": [
            "Use parameterized queries with placeholders",
            "Use ORM libraries like SQLAlchemy",
            "Validate and sanitize all user inputs",
            "Use database connection libraries with built-in protection",
        ],
    }

    logger.info(
        f"SQL injection analysis completed - Vulnerabilities: {len(vulnerabilities)}, Risk Level: {risk_level}"
    )
    logger.info("analyze_sql_injection function completed successfully")
    return json.dumps(result, indent=2)


def analyze_command_injection(code: str) -> str:
    """
    Analyze Python source code for command injection vulnerabilities and security risks.

    This function performs static code analysis to detect potential command injection
    vulnerabilities in Python code. It scans for dangerous patterns that could allow
    arbitrary command execution, such as using user input directly in system commands,
    shell execution functions, or subprocess calls without proper sanitization. The
    analysis helps identify security weaknesses that could lead to remote code execution.

    Args:
        code (str): The Python source code to analyze for command injection vulnerabilities.
                   Can be a single function, class, module, or complete script.
                   Examples: "os.system('ping ' + user_input)",
                            "subprocess.run(['ls', '-la', user_input])",
                            "subprocess.Popen(f'echo {user_data}', shell=True)"

    Returns:
        str: A JSON string containing command injection analysis results with the following structure:
        {
            "vulnerabilities": [                    // List of detected vulnerabilities
                {
                    "type": "Command Injection",   // String: vulnerability type
                    "description": "os.system with user input", // String: detailed description
                    "line": 25,                    // Integer: line number where vulnerability was found
                    "code": "os.system('ping ' + user_input)", // String: vulnerable code snippet
                    "severity": "high"             // String: "high", "medium", or "low"
                }
            ],
            "risk_level": "high",                  // String: overall risk assessment
            "vulnerability_count": 2,              // Integer: total number of vulnerabilities found
            "recommendations": [                   // List of security improvement suggestions
                "Use subprocess with shell=False and proper argument lists",
                "Validate and sanitize all user inputs",
                "Use specific command libraries instead of shell commands",
                "Implement proper input validation and whitelisting"
            ]
        }

        Risk levels are determined as follows:
        - Low: 0 vulnerabilities found
        - Medium: 1-2 vulnerabilities found
        - High: 3+ vulnerabilities found

    Raises:
        No exceptions are raised - all errors are returned in the JSON response.

    Examples:
        >>> code = '''
        ... def ping_host(host):
        ...     os.system(f"ping {host}")
        ... '''
        >>> result = analyze_command_injection(code)
        >>> data = json.loads(result)
        >>> print(f"Risk level: {data['risk_level']}")  # "high"
        >>> print(f"Vulnerabilities found: {data['vulnerability_count']}")  # 1

        >>> code = '''
        ... def list_directory(path):
        ...     subprocess.run(['ls', '-la', path], shell=False)
        ... '''
        >>> result = analyze_command_injection(code)
        >>> data = json.loads(result)
        >>> print(f"Risk level: {data['risk_level']}")  # "low"

    Notes:
        - Detects multiple command injection patterns including os.system, subprocess, and shell=True
        - Covers various dangerous functions: os.system, os.popen, subprocess.run, subprocess.Popen
        - Identifies shell=True usage which is particularly dangerous
        - Provides line numbers for easy vulnerability location
        - Includes severity assessment for each vulnerability
        - Offers actionable security recommendations
        - Uses regex patterns for pattern matching (case-insensitive)
        - Results are logged for monitoring and debugging purposes
        - This is static analysis - runtime behavior may differ
    """
    logger.info("Starting analyze_command_injection function")
    logger.info(f"Input code length: {len(code)} characters")

    command_injection_patterns = [
        # os.system with variables
        (r"os\.system\s*\(\s*[^)]*\+", "os.system with string concatenation"),
        (r'os\.system\s*\(\s*f["\']', "os.system with f-string"),
        (r"os\.system\s*\(\s*[^)]*\.format\(", "os.system with .format()"),
        # subprocess with shell=True
        (
            r"subprocess\.(?:call|run|Popen)\s*\([^)]*shell\s*=\s*True",
            "subprocess with shell=True",
        ),
        (
            r"subprocess\.(?:call|run|Popen)\s*\([^)]*\+",
            "subprocess with string concatenation",
        ),
        # eval and exec
        (r"eval\s*\(", "Use of eval() function"),
        (r"exec\s*\(", "Use of exec() function"),
        # __import__ with variables
        (r"__import__\s*\(\s*[^)]*\+", "__import__ with string concatenation"),
        (r'__import__\s*\(\s*f["\']', "__import__ with f-string"),
        # globals and locals
        (r"globals\s*\(", "Use of globals() function"),
        (r"locals\s*\(", "Use of locals() function"),
    ]

    vulnerabilities = []
    risk_level = "low"

    for pattern, description in command_injection_patterns:
        matches = re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            line_num = code[: match.start()].count("\n") + 1
            vulnerabilities.append(
                {
                    "type": "Command Injection",
                    "description": description,
                    "line": line_num,
                    "code": (
                        match.group(0)[:100] + "..."
                        if len(match.group(0)) > 100
                        else match.group(0)
                    ),
                    "severity": "high",
                }
            )

    if vulnerabilities:
        risk_level = "high" if len(vulnerabilities) > 2 else "medium"

    result = {
        "vulnerabilities": vulnerabilities,
        "risk_level": risk_level,
        "vulnerability_count": len(vulnerabilities),
        "recommendations": [
            "Avoid using eval(), exec(), globals(), locals()",
            "Use subprocess with shell=False and proper argument lists",
            "Validate and sanitize all command inputs",
            "Use specific libraries instead of shell commands",
            "Consider using shlex.quote() for shell arguments",
        ],
    }

    logger.info(
        f"Command injection analysis completed - Vulnerabilities: {len(vulnerabilities)}, Risk Level: {risk_level}"
    )
    logger.info("analyze_command_injection function completed successfully")
    return json.dumps(result, indent=2)


def analyze_hardcoded_secrets(code: str) -> str:
    """
    Analyze code for hardcoded secrets and sensitive information.

    Args:
        code (str): The source code to analyze

    Returns:
        str: JSON string with hardcoded secrets analysis
    """
    logger.info("Starting analyze_hardcoded_secrets function")
    logger.info(f"Input code length: {len(code)} characters")

    secret_patterns = [
        # Common secret variable names
        (
            r'(?:password|passwd|pwd)\s*=\s*["\'][^"\']+["\']',
            "Hardcoded password",
        ),
        (
            r'(?:api_key|apikey|key)\s*=\s*["\'][^"\']+["\']',
            "Hardcoded API key",
        ),
        (r'(?:secret|secret_key)\s*=\s*["\'][^"\']+["\']', "Hardcoded secret"),
        (r'(?:token|access_token)\s*=\s*["\'][^"\']+["\']', "Hardcoded token"),
        (
            r'(?:private_key|privatekey)\s*=\s*["\'][^"\']+["\']',
            "Hardcoded private key",
        ),
        (
            r'(?:database_url|db_url|connection_string)\s*=\s*["\'][^"\']+["\']',
            "Hardcoded database URL",
        ),
        # Common secret values
        (r'["\'](?:sk_|pk_)[a-zA-Z0-9]{20,}["\']', "Potential Stripe API key"),
        (
            r'["\'](?:AKIA|A3T|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}["\']',
            "Potential AWS access key",
        ),
        (r'["\'][a-zA-Z0-9]{32,}["\']', "Potential hash or token"),
        # Database credentials
        (
            r'["\'](?:mysql|postgresql|mongodb)://[^"\']+["\']',
            "Hardcoded database connection string",
        ),
        # Email credentials
        (
            r'(?:email_password|smtp_password)\s*=\s*["\'][^"\']+["\']',
            "Hardcoded email password",
        ),
    ]

    vulnerabilities = []
    risk_level = "low"

    for pattern, description in secret_patterns:
        matches = re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            line_num = code[: match.start()].count("\n") + 1
            # Mask the actual value for security
            masked_code = re.sub(
                r'["\'][^"\']+["\']', '"***MASKED***"', match.group(0)
            )
            vulnerabilities.append(
                {
                    "type": "Hardcoded Secret",
                    "description": description,
                    "line": line_num,
                    "code": masked_code,
                    "severity": "high",
                }
            )

    if vulnerabilities:
        risk_level = "high" if len(vulnerabilities) > 2 else "medium"

    result = {
        "vulnerabilities": vulnerabilities,
        "risk_level": risk_level,
        "vulnerability_count": len(vulnerabilities),
        "recommendations": [
            "Use environment variables for sensitive data",
            "Use configuration management tools",
            "Use secret management services",
            "Never commit secrets to version control",
            "Use .env files (not committed) for local development",
        ],
    }

    logger.info(
        f"Hardcoded secrets analysis completed - Vulnerabilities: {len(vulnerabilities)}, Risk Level: {risk_level}"
    )
    logger.info("analyze_hardcoded_secrets function completed successfully")
    return json.dumps(result, indent=2)


def analyze_path_traversal(code: str) -> str:
    """
    Analyze code for path traversal vulnerabilities.

    Args:
        code (str): The source code to analyze

    Returns:
        str: JSON string with path traversal analysis
    """
    path_traversal_patterns = [
        # File operations with user input
        (r"open\s*\(\s*[^)]*\+", "open() with string concatenation"),
        (r'open\s*\(\s*f["\']', "open() with f-string"),
        (r"open\s*\(\s*[^)]*\.format\(", "open() with .format()"),
        # os.path operations
        (
            r"os\.path\.join\s*\(\s*[^)]*\+",
            "os.path.join with string concatenation",
        ),
        (
            r"os\.path\.(?:exists|isfile|isdir)\s*\(\s*[^)]*\+",
            "os.path check with string concatenation",
        ),
        # File operations without path validation
        (
            r"with\s+open\s*\(\s*[^)]*\+\s*[^)]*\)",
            "File operation with concatenated path",
        ),
        # Directory traversal patterns
        (r'["\']\.\./', "Relative path with parent directory"),
        (r'["\']\.\.\\', "Relative path with parent directory (Windows)"),
    ]

    vulnerabilities = []
    risk_level = "low"

    for pattern, description in path_traversal_patterns:
        matches = re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            line_num = code[: match.start()].count("\n") + 1
            vulnerabilities.append(
                {
                    "type": "Path Traversal",
                    "description": description,
                    "line": line_num,
                    "code": (
                        match.group(0)[:100] + "..."
                        if len(match.group(0)) > 100
                        else match.group(0)
                    ),
                    "severity": "medium",
                }
            )

    if vulnerabilities:
        risk_level = "high" if len(vulnerabilities) > 3 else "medium"

    result = {
        "vulnerabilities": vulnerabilities,
        "risk_level": risk_level,
        "vulnerability_count": len(vulnerabilities),
        "recommendations": [
            "Use os.path.abspath() and os.path.realpath() to normalize paths",
            "Validate file paths against allowed directories",
            "Use pathlib.Path for safer path operations",
            "Implement proper input validation and sanitization",
            "Use chroot or jail environments when possible",
        ],
    }

    return json.dumps(result, indent=2)


def analyze_unsafe_deserialization(code: str) -> str:
    """
    Analyze code for unsafe deserialization vulnerabilities.

    Args:
        code (str): The source code to analyze

    Returns:
        str: JSON string with deserialization analysis
    """
    deserialization_patterns = [
        # Pickle (very dangerous)
        (r"pickle\.loads\s*\(", "Use of pickle.loads()"),
        (r"pickle\.load\s*\(", "Use of pickle.load()"),
        # YAML with Loader
        (r"yaml\.load\s*\(", "Use of yaml.load() without safe loader"),
        (
            r"yaml\.load\s*\([^)]*Loader\s*=\s*yaml\.Loader",
            "Use of yaml.load() with unsafe Loader",
        ),
        # JSON with object_hook
        (
            r"json\.loads\s*\([^)]*object_hook",
            "json.loads with custom object_hook",
        ),
        # marshal
        (r"marshal\.loads\s*\(", "Use of marshal.loads()"),
        (r"marshal\.load\s*\(", "Use of marshal.load()"),
    ]

    vulnerabilities = []
    risk_level = "low"

    for pattern, description in deserialization_patterns:
        matches = re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            line_num = code[: match.start()].count("\n") + 1
            vulnerabilities.append(
                {
                    "type": "Unsafe Deserialization",
                    "description": description,
                    "line": line_num,
                    "code": (
                        match.group(0)[:100] + "..."
                        if len(match.group(0)) > 100
                        else match.group(0)
                    ),
                    "severity": "high",
                }
            )

    if vulnerabilities:
        risk_level = "high" if len(vulnerabilities) > 1 else "medium"

    result = {
        "vulnerabilities": vulnerabilities,
        "risk_level": risk_level,
        "vulnerability_count": len(vulnerabilities),
        "recommendations": [
            "Avoid using pickle for untrusted data",
            "Use yaml.safe_load() instead of yaml.load()",
            "Validate all deserialized data",
            "Use custom serialization formats for sensitive data",
            "Consider using libraries like pydantic for data validation",
        ],
    }

    return json.dumps(result, indent=2)


def analyze_xss_vulnerabilities(code: str) -> str:
    """
    Analyze code for potential XSS vulnerabilities in web applications.

    Args:
        code (str): The source code to analyze

    Returns:
        str: JSON string with XSS analysis
    """
    xss_patterns = [
        # Flask/Jinja2 template injection
        (
            r"return\s+render_template\s*\(\s*[^)]*\+",
            "Template rendering with string concatenation",
        ),
        (
            r"return\s+render_template_string\s*\(\s*[^)]*\+",
            "Template string rendering with concatenation",
        ),
        # Django template injection
        (
            r"return\s+render\s*\(\s*request\s*,\s*[^)]*\+",
            "Django render with string concatenation",
        ),
        # HTML generation with user input
        (
            r'f["\']<[^>]*>{[^}]*}[^>]*>["\']',
            "F-string HTML with variable interpolation",
        ),
        (r'["\']<[^>]*>\s*\+\s*[^+]+["\']', "HTML with string concatenation"),
        # JavaScript injection
        (
            r'f["\']<script[^>]*>{[^}]*}[^>]*>["\']',
            "F-string script tag with variable",
        ),
        (
            r'["\']<script[^>]*>\s*\+\s*[^+]+["\']',
            "Script tag with string concatenation",
        ),
    ]

    vulnerabilities = []
    risk_level = "low"

    for pattern, description in xss_patterns:
        matches = re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            line_num = code[: match.start()].count("\n") + 1
            vulnerabilities.append(
                {
                    "type": "Cross-Site Scripting (XSS)",
                    "description": description,
                    "line": line_num,
                    "code": (
                        match.group(0)[:100] + "..."
                        if len(match.group(0)) > 100
                        else match.group(0)
                    ),
                    "severity": "high",
                }
            )

    if vulnerabilities:
        risk_level = "high" if len(vulnerabilities) > 2 else "medium"

    result = {
        "vulnerabilities": vulnerabilities,
        "risk_level": risk_level,
        "vulnerability_count": len(vulnerabilities),
        "recommendations": [
            "Use template engines with automatic escaping",
            "Validate and sanitize all user inputs",
            "Use Content Security Policy (CSP) headers",
            "Escape output in templates",
            "Use libraries like bleach for HTML sanitization",
        ],
    }

    return json.dumps(result, indent=2)


def analyze_input_validation(code: str) -> str:
    """
    Analyze code for input validation issues.

    Args:
        code (str): The source code to analyze

    Returns:
        str: JSON string with input validation analysis
    """
    validation_patterns = [
        # Direct use of user input without validation
        (r"input\s*\(\s*\)", "Use of input() without validation"),
        (
            r"request\.(?:args|form|json)\s*\[[^\]]+\]",
            "Direct access to request data",
        ),
        (
            r"request\.(?:args|form|json)\.get\s*\([^)]*\)",
            "Request data access without validation",
        ),
        # Weak validation patterns
        (r"if\s+len\s*\(\s*[^)]+\s*\)\s*>\s*0:", "Length-only validation"),
        (r"if\s+[^)]+\s*is\s+not\s+None:", "None-only validation"),
        # Missing validation in critical operations
        (r"open\s*\(\s*[^)]*\)", "File operation without input validation"),
        (
            r"subprocess\.[a-zA-Z]+\s*\(\s*[^)]*\)",
            "Subprocess without input validation",
        ),
    ]

    vulnerabilities = []
    risk_level = "low"

    for pattern, description in validation_patterns:
        matches = re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            line_num = code[: match.start()].count("\n") + 1
            vulnerabilities.append(
                {
                    "type": "Input Validation",
                    "description": description,
                    "line": line_num,
                    "code": (
                        match.group(0)[:100] + "..."
                        if len(match.group(0)) > 100
                        else match.group(0)
                    ),
                    "severity": "medium",
                }
            )

    if vulnerabilities:
        risk_level = "high" if len(vulnerabilities) > 5 else "medium"

    result = {
        "vulnerabilities": vulnerabilities,
        "risk_level": risk_level,
        "vulnerability_count": len(vulnerabilities),
        "recommendations": [
            "Implement comprehensive input validation",
            "Use type hints and validation libraries like pydantic",
            "Validate data types, ranges, and formats",
            "Use allowlists instead of blocklists",
            "Implement proper error handling for invalid inputs",
        ],
    }

    return json.dumps(result, indent=2)


def comprehensive_security_analysis(code: str) -> str:
    """
    Perform comprehensive security analysis on Python code.

    Args:
        code (str): The source code to analyze

    Returns:
        str: JSON string with comprehensive security analysis
    """
    # Run all security checks
    sql_result = json.loads(analyze_sql_injection(code))
    command_result = json.loads(analyze_command_injection(code))
    secrets_result = json.loads(analyze_hardcoded_secrets(code))
    path_result = json.loads(analyze_path_traversal(code))
    deserialization_result = json.loads(analyze_unsafe_deserialization(code))
    xss_result = json.loads(analyze_xss_vulnerabilities(code))
    validation_result = json.loads(analyze_input_validation(code))

    # Combine all vulnerabilities
    all_vulnerabilities = (
        sql_result["vulnerabilities"]
        + command_result["vulnerabilities"]
        + secrets_result["vulnerabilities"]
        + path_result["vulnerabilities"]
        + deserialization_result["vulnerabilities"]
        + xss_result["vulnerabilities"]
        + validation_result["vulnerabilities"]
    )

    # Calculate overall risk level
    high_severity = len(
        [v for v in all_vulnerabilities if v["severity"] == "high"]
    )
    medium_severity = len(
        [v for v in all_vulnerabilities if v["severity"] == "medium"]
    )

    if high_severity > 0:
        overall_risk = "high"
    elif medium_severity > 3:
        overall_risk = "medium"
    else:
        overall_risk = "low"

    # Calculate security score
    total_vulnerabilities = len(all_vulnerabilities)
    security_score = max(
        0, 100 - (high_severity * 20) - (medium_severity * 10)
    )

    # Group vulnerabilities by type
    vulnerability_types: Dict[str, List[Dict[str, Any]]] = {}
    for vuln in all_vulnerabilities:
        vuln_type = vuln["type"]
        if vuln_type not in vulnerability_types:
            vulnerability_types[vuln_type] = []
        vulnerability_types[vuln_type].append(vuln)

    result = {
        "overall_risk_level": overall_risk,
        "security_score": security_score,
        "total_vulnerabilities": total_vulnerabilities,
        "high_severity_count": high_severity,
        "medium_severity_count": medium_severity,
        "vulnerability_types": vulnerability_types,
        "all_vulnerabilities": all_vulnerabilities,
        "summary": {
            "sql_injection": len(sql_result["vulnerabilities"]),
            "command_injection": len(command_result["vulnerabilities"]),
            "hardcoded_secrets": len(secrets_result["vulnerabilities"]),
            "path_traversal": len(path_result["vulnerabilities"]),
            "unsafe_deserialization": len(
                deserialization_result["vulnerabilities"]
            ),
            "xss": len(xss_result["vulnerabilities"]),
            "input_validation": len(validation_result["vulnerabilities"]),
        },
        "recommendations": [
            "Address high-severity vulnerabilities first",
            "Implement secure coding practices",
            "Use security-focused libraries and frameworks",
            "Regular security audits and code reviews",
            "Follow OWASP guidelines",
            "Use automated security testing tools",
        ],
    }

    return json.dumps(result, indent=2)


# Create individual interfaces for each function
sql_injection_demo = gr.Interface(
    fn=analyze_sql_injection,
    inputs=gr.Textbox(
        placeholder="Enter Python code to analyze for SQL injection vulnerabilities...",
        label="Python Code",
        lines=10,
    ),
    outputs=gr.JSON(label="SQL Injection Analysis"),
    title="SQL Injection Vulnerability Scanner",
    description="Analyze code for SQL injection vulnerabilities including f-string queries, string concatenation, and format strings.",
    examples=[
        [
            """query = f"SELECT * FROM users WHERE id = {user_id}"
cursor.execute(query)"""
        ],
        [
            """sql = "INSERT INTO logs VALUES (" + log_data + ")"
cursor.execute(sql)"""
        ],
        [
            """query = "SELECT * FROM users WHERE name = %s"
cursor.execute(query, (user_name,))"""
        ],
    ],
)

command_injection_demo = gr.Interface(
    fn=analyze_command_injection,
    inputs=gr.Textbox(
        placeholder="Enter Python code to analyze for command injection vulnerabilities...",
        label="Python Code",
        lines=10,
    ),
    outputs=gr.JSON(label="Command Injection Analysis"),
    title="Command Injection Vulnerability Scanner",
    description="Analyze code for command injection vulnerabilities including os.system, subprocess, eval, and exec usage.",
    examples=[
        [
            """import os
os.system(f"ping {user_input}")"""
        ],
        [
            """import subprocess
subprocess.run(command, shell=True)"""
        ],
        ["""eval(user_code)"""],
    ],
)

hardcoded_secrets_demo = gr.Interface(
    fn=analyze_hardcoded_secrets,
    inputs=gr.Textbox(
        placeholder="Enter Python code to analyze for hardcoded secrets...",
        label="Python Code",
        lines=10,
    ),
    outputs=gr.JSON(label="Hardcoded Secrets Analysis"),
    title="Hardcoded Secrets Scanner",
    description="Analyze code for hardcoded passwords, API keys, tokens, and other sensitive information.",
    examples=[
        [
            """password = "secret123"
api_key = "sk-1234567890abcdef"
database_url = "postgresql://user:pass@localhost/db" """
        ],
        [
            """import os
password = os.getenv('DB_PASSWORD')
api_key = os.getenv('API_KEY')"""
        ],
    ],
)

path_traversal_demo = gr.Interface(
    fn=analyze_path_traversal,
    inputs=gr.Textbox(
        placeholder="Enter Python code to analyze for path traversal vulnerabilities...",
        label="Python Code",
        lines=10,
    ),
    outputs=gr.JSON(label="Path Traversal Analysis"),
    title="Path Traversal Vulnerability Scanner",
    description="Analyze code for path traversal vulnerabilities in file operations.",
    examples=[
        [
            """with open(user_input, 'r') as f:
    content = f.read()"""
        ],
        [
            """import os
safe_path = os.path.abspath(user_input)
if safe_path.startswith('/allowed/directory'):
    with open(safe_path, 'r') as f:
        content = f.read()"""
        ],
    ],
)

unsafe_deserialization_demo = gr.Interface(
    fn=analyze_unsafe_deserialization,
    inputs=gr.Textbox(
        placeholder="Enter Python code to analyze for unsafe deserialization...",
        label="Python Code",
        lines=10,
    ),
    outputs=gr.JSON(label="Unsafe Deserialization Analysis"),
    title="Unsafe Deserialization Scanner",
    description="Analyze code for unsafe deserialization patterns including pickle, yaml.load, and custom object hooks.",
    examples=[
        [
            """import pickle
data = pickle.loads(user_input)"""
        ],
        [
            """import yaml
data = yaml.safe_load(user_input)"""
        ],
        [
            """import json
data = json.loads(user_input)"""
        ],
    ],
)

comprehensive_demo = gr.Interface(
    fn=comprehensive_security_analysis,
    inputs=gr.Textbox(
        placeholder="Enter Python code for comprehensive security analysis...",
        label="Python Code",
        lines=10,
    ),
    outputs=gr.JSON(label="Comprehensive Security Analysis"),
    title="Comprehensive Security Scanner",
    description="Perform comprehensive security analysis covering all vulnerability types with risk assessment and scoring.",
    examples=[
        [
            """query = f"SELECT * FROM users WHERE id = {user_id}"
os.system(f"ping {user_input}")
password = "secret123"
import pickle
data = pickle.loads(user_input)"""
        ]
    ],
)

# Create tabbed interface
demo = gr.TabbedInterface(
    [
        sql_injection_demo,
        command_injection_demo,
        hardcoded_secrets_demo,
        path_traversal_demo,
        unsafe_deserialization_demo,
        comprehensive_demo,
    ],
    [
        "SQL Injection",
        "Command Injection",
        "Hardcoded Secrets",
        "Path Traversal",
        "Unsafe Deserialization",
        "Comprehensive",
    ],
    title="Code Security Analysis Server",
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
