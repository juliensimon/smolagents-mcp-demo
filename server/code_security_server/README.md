# Code Security Server - Vulnerability Analysis

A comprehensive MCP server implementation for security vulnerability analysis and code security assessment. This server provides 6 different security analysis functions covering SQL injection, command injection, hardcoded secrets, path traversal, unsafe deserialization, and comprehensive security scanning.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Required packages: `gradio`, `re`

### Installation
```bash
# Install required packages
pip install gradio

# Navigate to the code security server directory
cd server/code_security_server
```

### Launch Server
```bash
python code_security_server.py
```
**Server Port:** 7865
**Access:** http://localhost:7865



## 📋 Features

### Server Functionality
The server provides 6 comprehensive security analysis functions:

1. **SQL Injection Analysis**
   - F-string SQL query detection
   - String concatenation SQL detection
   - Format string SQL detection
   - Parameterized query recommendations

2. **Command Injection Analysis**
   - os.system vulnerability detection
   - subprocess with shell=True detection
   - eval() and exec() usage detection
   - Dynamic import detection

3. **Hardcoded Secrets Analysis**
   - Password variable detection
   - API key detection
   - Secret key detection
   - Token detection
   - Database URL detection

4. **Path Traversal Analysis**
   - File operation vulnerability detection
   - Path validation issues
   - Directory traversal patterns
   - Safe path handling recommendations

5. **Unsafe Deserialization Analysis**
   - pickle usage detection
   - yaml.load() detection
   - json.loads() with untrusted data
   - Deserialization best practices

6. **Comprehensive Security Analysis**
   - All vulnerability types combined
   - Risk level assessment
   - Priority-based recommendations
   - Security score calculation



## 🎯 Usage Examples

### SQL Injection Analysis
```python
# Example vulnerable code
code = """
query = f"SELECT * FROM users WHERE id = {user_id}"
result = cursor.execute("INSERT INTO logs VALUES (" + log_data + ")")
"""

# Expected result:
{
  "vulnerabilities": [
    {
      "type": "SQL Injection",
      "description": "F-string SQL query with variable interpolation",
      "line": 2,
      "code": "f\"SELECT * FROM users WHERE id = {user_id}\"",
      "severity": "high"
    },
    {
      "type": "SQL Injection",
      "description": "SQL query with string concatenation",
      "line": 3,
      "code": "\"INSERT INTO logs VALUES (\" + log_data + \")\"",
      "severity": "high"
    }
  ],
  "risk_level": "high",
  "vulnerability_count": 2,
  "recommendations": [
    "Use parameterized queries with placeholders",
    "Use ORM libraries like SQLAlchemy",
    "Validate and sanitize all user inputs"
  ]
}
```

### Command Injection Analysis
```python
# Example vulnerable code
code = """
os.system(f"ping {user_input}")
subprocess.run(command, shell=True)
eval(user_code)
"""

# Expected result:
{
  "vulnerabilities": [
    {
      "type": "Command Injection",
      "description": "os.system with f-string",
      "line": 2,
      "code": "os.system(f\"ping {user_input}\")",
      "severity": "high"
    },
    {
      "type": "Command Injection",
      "description": "subprocess with shell=True",
      "line": 3,
      "code": "subprocess.run(command, shell=True)",
      "severity": "high"
    },
    {
      "type": "Command Injection",
      "description": "Use of eval() function",
      "line": 4,
      "code": "eval(user_code)",
      "severity": "high"
    }
  ],
  "risk_level": "high",
  "recommendations": [
    "Avoid using eval(), exec(), globals(), locals()",
    "Use subprocess with shell=False and proper argument lists",
    "Validate and sanitize all command inputs"
  ]
}
```

### Hardcoded Secrets Analysis
```python
# Example vulnerable code
code = """
password = "secret123"
api_key = "sk-1234567890abcdef"
database_url = "postgresql://user:pass@localhost/db"
"""

# Expected result:
{
  "vulnerabilities": [
    {
      "type": "Hardcoded Secret",
      "description": "Hardcoded password",
      "line": 2,
      "code": "password = \"***MASKED***\"",
      "severity": "high"
    },
    {
      "type": "Hardcoded Secret",
      "description": "Hardcoded API key",
      "line": 3,
      "code": "api_key = \"***MASKED***\"",
      "severity": "high"
    },
    {
      "type": "Hardcoded Secret",
      "description": "Hardcoded database URL",
      "line": 4,
      "code": "database_url = \"***MASKED***\"",
      "severity": "high"
    }
  ],
  "risk_level": "high",
  "recommendations": [
    "Use environment variables for sensitive data",
    "Use configuration management tools",
    "Use secret management services"
  ]
}
```

## 🔧 Configuration

### Server Configuration
The server uses comprehensive logging and security analysis:

```python
# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('code_security_server.log'),
        logging.StreamHandler()
    ]
)
```

### Test Client Configuration
The test client uses `config.json` for MCP server communication:

```json
{
  "server": {
    "url": "http://127.0.0.1:7865/gradio_api/mcp/sse"
  },
  "model": {
    "default": "arcee-ai/coder-large",
    "api_base": "https://api.together.xyz/v1",
    "configs": {
      "arcee-ai/coder-large": {
        "temperature": 0.1,
        "max_tokens": 2000,
        "top_p": 0.9,
        "top_k": 40,
        "repetition_penalty": 1.1,
        "system_prompt": "You are a helpful AI assistant specialized in code security analysis..."
      }
    }
  }
}
```

## 🌐 Interface Features

### Server Interface
- **Multi-function Support**: 6 different security analysis functions
- **JSON Output**: Structured security analysis results
- **Error Handling**: Comprehensive error management
- **Logging**: Detailed operation logging

### Test Client Interface
- **SQL Injection Tab**: SQL vulnerability detection
- **Command Injection Tab**: Command execution vulnerability detection
- **Hardcoded Secrets Tab**: Secret detection and masking
- **Path Traversal Tab**: File path vulnerability detection
- **Unsafe Deserialization Tab**: Deserialization vulnerability detection
- **Comprehensive Security Tab**: All vulnerability types combined
- **Examples & Documentation Tab**: Security best practices

### Interactive Elements
- **Code Input**: Large text areas for code input
- **Analysis Selection**: Multiple security analysis types
- **JSON Outputs**: Structured results display
- **Examples**: Pre-filled vulnerable code examples
- **Risk Level Indicators**: Visual risk assessment

## 📊 API Reference

### Core Security Functions

#### 1. SQL Injection Analysis
```python
def analyze_sql_injection(code: str) -> str:
    """
    Analyze code for SQL injection vulnerabilities.

    Args:
        code (str): The source code to analyze

    Returns:
        str: JSON string with SQL injection analysis
    """
```

#### 2. Command Injection Analysis
```python
def analyze_command_injection(code: str) -> str:
    """
    Analyze code for command injection vulnerabilities.

    Args:
        code (str): The source code to analyze

    Returns:
        str: JSON string with command injection analysis
    """
```

#### 3. Hardcoded Secrets Analysis
```python
def analyze_hardcoded_secrets(code: str) -> str:
    """
    Analyze code for hardcoded secrets and sensitive information.

    Args:
        code (str): The source code to analyze

    Returns:
        str: JSON string with hardcoded secrets analysis
    """
```

#### 4. Path Traversal Analysis
```python
def analyze_path_traversal(code: str) -> str:
    """
    Analyze code for path traversal vulnerabilities.

    Args:
        code (str): The source code to analyze

    Returns:
        str: JSON string with path traversal analysis
    """
```

#### 5. Unsafe Deserialization Analysis
```python
def analyze_unsafe_deserialization(code: str) -> str:
    """
    Analyze code for unsafe deserialization vulnerabilities.

    Args:
        code (str): The source code to analyze

    Returns:
        str: JSON string with unsafe deserialization analysis
    """
```

#### 6. Comprehensive Security Analysis
```python
def comprehensive_security_analysis(code: str) -> str:
    """
    Perform comprehensive security analysis covering all vulnerability types.

    Args:
        code (str): The source code to analyze

    Returns:
        str: JSON string with comprehensive security analysis
    """
```

### Response Formats

#### Security Analysis Response
```json
{
  "vulnerabilities": [
    {
      "type": "SQL Injection",
      "description": "F-string SQL query with variable interpolation",
      "line": 10,
      "code": "f\"SELECT * FROM users WHERE id = {user_id}\"",
      "severity": "high"
    }
  ],
  "risk_level": "high",
  "vulnerability_count": 1,
  "recommendations": [
    "Use parameterized queries with placeholders",
    "Use ORM libraries like SQLAlchemy",
    "Validate and sanitize all user inputs"
  ]
}
```

#### Comprehensive Analysis Response
```json
{
  "sql_injection": {
    "vulnerabilities": [...],
    "risk_level": "medium"
  },
  "command_injection": {
    "vulnerabilities": [...],
    "risk_level": "high"
  },
  "hardcoded_secrets": {
    "vulnerabilities": [...],
    "risk_level": "low"
  },
  "overall_risk_level": "high",
  "total_vulnerabilities": 5,
  "security_score": 65
}
```

## 🔍 Logging

The server includes comprehensive logging for monitoring and debugging:

### Log File
- **Location**: `code_security_server.log`
- **Format**: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- **Level**: INFO

### Log Entries
```
2025-07-21 14:22:05,840 - code_security_server - INFO - Starting analyze_sql_injection function
2025-07-21 14:22:05,840 - code_security_server - INFO - Input code length: 150 characters
2025-07-21 14:22:05,841 - code_security_server - INFO - SQL injection analysis completed - Vulnerabilities: 2, Risk Level: high
2025-07-21 14:22:05,841 - code_security_server - INFO - analyze_sql_injection function completed successfully
```

## 🚨 Troubleshooting

### Common Issues

**1. Port Already in Use**
```bash
# Check if port is in use
lsof -i :7865

# Kill process using the port
kill -9 <PID>
```

**2. Missing Dependencies**
```bash
# Install missing packages
pip install gradio
```

**3. False Positives**
```bash
# Review vulnerability patterns
# Check code context
# Verify security implications
```

### Error Messages

**"Analysis failed"**
- Check input code format
- Verify code is valid
- Review error logs for details

**"No vulnerabilities found"**
- Code may be secure
- Check different analysis types
- Review security best practices

## 🔄 Integration

### MCP Protocol Support
The server implements the Model Context Protocol for AI-powered interactions:

- **Tool Registration**: Automatic tool discovery
- **JSON Communication**: Structured data exchange
- **Error Handling**: Robust error management
- **Logging**: Comprehensive operation logging

### Client Integration
```python
# Example client usage
from smolagents import MCPClient

# Connect to server
client = MCPClient({"url": "http://127.0.0.1:7865/gradio_api/mcp/sse"})

# Get available tools
tools = client.get_tools()

# Use SQL injection analysis
result = client.call_tool("analyze_sql_injection", {"code": "query = f\"SELECT * FROM users WHERE id = {user_id}\""})
```

## 📈 Performance

### Processing Speed
- **Small code (< 100 lines)**: ~50-200ms
- **Medium code (100-1000 lines)**: ~200ms-1s
- **Large code (> 1000 lines)**: ~1-5s

### Memory Usage
- **Efficient regex processing**: Minimal memory overhead
- **Stream-based analysis**: Memory-efficient operations
- **No persistent storage**: Stateless operation

## 🔒 Security

### Input Validation
- All code inputs are validated
- Maximum code size limits
- Safe regex processing

### Local Processing
- No external API calls for analysis
- Local security pattern matching
- No code transmission to external services

## 🤝 Contributing

### Development Setup
1. Clone the repository
2. Install dependencies: `pip install gradio`
3. Run tests: `python -m pytest tests/`
4. Start development server: `python code_security_server.py`

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings for all functions
- Include error handling

### Testing
- Test with various vulnerability types
- Verify error handling
- Check edge cases
- Validate output formats

## 📚 Additional Resources

### Documentation
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Gradio Documentation](https://gradio.app/docs/)
- [MCP Protocol](https://modelcontextprotocol.io/)

### Related Projects
- [Bandit](https://bandit.readthedocs.io/)
- [Safety](https://pyup.io/safety/)
- [Semgrep](https://semgrep.dev/)

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review error messages carefully
3. Verify configuration settings
4. Test with simple examples first
5. Check server logs for detailed information

---

**Note:** This server is designed for development and testing purposes. For production use, ensure proper security measures and error handling are implemented.
