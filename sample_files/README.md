# Sample Files with Defects

This directory contains Python files with intentionally introduced defects for testing code analysis tools, security scanners, and quality assessment systems.

## Purpose

These files are designed to test the effectiveness of:
- Static code analysis tools
- Security vulnerability scanners
- Code quality assessment tools
- Linting and formatting tools
- Documentation generators

## Files Overview

### 1. `user_management.py`
A user management system with authentication and database operations.

**Defects included:**
- Weak password hashing (MD5 with static salt)
- SQL injection vulnerabilities
- Race conditions in user creation
- Serialization vulnerabilities (pickle)
- Weak password policy (minimum 3 characters)
- Exposed password hashes
- No input validation
- Poor error handling

### 2. `data_processor.py`
A data processing utility for CSV files with statistical analysis.

**Defects included:**
- Memory leaks (global cache)
- Command injection vulnerabilities
- Insecure temporary file creation
- Dangerous eval usage
- Inefficient algorithms
- No file existence validation
- Poor error handling
- Unused imports

### 3. `web_api.py`
A Flask web API with user management and file operations.

**Defects included:**
- Multiple SQL injection vulnerabilities
- Command injection
- Path traversal vulnerabilities
- Dangerous deserialization (pickle)
- Open redirect vulnerabilities
- No authentication checks
- Hardcoded credentials
- Session management issues
- File upload vulnerabilities
- System log exposure

### 4. `calculator.py`
A command-line calculator with history and memory features.

**Defects included:**
- Dangerous eval usage
- Command execution vulnerabilities
- Dangerous pickle serialization
- Inefficient recursive algorithms
- No file path validation
- Weak "encryption" (base64)
- Poor error handling
- Unused imports

### 5. `file_manager.py`
A comprehensive file management system with various operations.

**Defects included:**
- Extremely dangerous system operations (format, mount, useradd)
- Command injection vulnerabilities
- Weak encryption (base64)
- Dangerous pickle usage
- No URL validation
- Symlink vulnerabilities
- Path traversal risks
- No input validation

## Defect Categories

### Security Vulnerabilities
- **SQL Injection**: String formatting in database queries
- **Command Injection**: Shell command execution with user input
- **Path Traversal**: Unvalidated file paths
- **Deserialization**: Dangerous pickle usage
- **Open Redirect**: Unvalidated URLs
- **Weak Cryptography**: Base64 encoding as "encryption"
- **Hardcoded Credentials**: Secrets in source code

### Code Quality Issues
- **Poor Error Handling**: Bare except clauses
- **Unused Imports**: Unnecessary module imports
- **Inefficient Algorithms**: Recursive implementations without memoization
- **Memory Leaks**: Global variables accumulating data
- **Race Conditions**: Missing thread synchronization
- **No Input Validation**: Missing parameter checks

### Documentation Issues
- **Missing Docstrings**: No function documentation
- **No Type Hints**: Missing type annotations
- **Poor Comments**: Inadequate code documentation

### Performance Issues
- **Inefficient Data Structures**: Poor algorithm choices
- **Memory Inefficiency**: Unnecessary data copying
- **Resource Leaks**: Unclosed file handles

## Usage

These files are intended for testing purposes only. **Do not use in production environments.**

### Testing Code Analysis Tools

```bash
# Test with flake8
flake8 sample_files/

# Test with bandit (security)
bandit -r sample_files/

# Test with mypy (type checking)
mypy sample_files/

# Test with black (formatting)
black sample_files/

# Test with pylint
pylint sample_files/
```

### Testing Security Scanners

```bash
# Test with safety
safety check

# Test with semgrep
semgrep --config=auto sample_files/

# Test with bandit
bandit -r sample_files/ -f json
```

## Warning

⚠️ **IMPORTANT**: These files contain intentionally dangerous code patterns and should never be executed in a production environment or on systems with sensitive data. They are designed solely for testing and educational purposes.

## Contributing

When adding new sample files:
1. Include a variety of defect types
2. Use realistic but safe examples
3. Document the specific defects included
4. Ensure the code is syntactically valid Python
5. Add appropriate warnings about security risks

## License

This code is provided for educational and testing purposes only. Use at your own risk.
