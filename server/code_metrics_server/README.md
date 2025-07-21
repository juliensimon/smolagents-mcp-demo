# Code Metrics Server - Advanced Code Analysis

A comprehensive MCP server implementation for advanced code analysis and quality assessment. This server provides 10 different analysis functions covering complexity, style, security, performance, and maintainability metrics.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Required packages: `gradio`, `ast`, `logging`

### Installation
```bash
# Install required packages
pip install gradio

# Navigate to the code metrics server directory
cd server/code_metrics_server
```

### Launch Server
```bash
python code_metrics_server.py
```
**Server Port:** 7862
**Access:** http://localhost:7862

### Launch Test Client
```bash
python test_client.py
```
**Test Client Port:** 7862
**Access:** http://localhost:7862

## 📋 Features

### Server Functionality
The server provides 10 comprehensive code analysis functions:

1. **Code Complexity Analysis**
   - Cyclomatic complexity calculation
   - Function and class counting
   - Complexity level assessment (low/medium/high)

2. **Code Style Analysis**
   - Line length checking
   - Trailing whitespace detection
   - Style issue identification

3. **Code Coverage Metrics**
   - Coverage calculation simulation
   - Uncovered code identification
   - Coverage recommendations

4. **Naming Convention Analysis**
   - Variable naming patterns
   - Function naming conventions
   - Class naming standards

5. **Maintainability Index**
   - Code maintainability scoring
   - Complexity factors
   - Improvement suggestions

6. **Security Pattern Analysis**
   - Security vulnerability detection
   - Risk assessment
   - Security recommendations

7. **Performance Metrics**
   - Performance bottleneck identification
   - Optimization opportunities
   - Performance scoring

8. **Documentation Quality**
   - Docstring analysis
   - Comment coverage
   - Documentation completeness

9. **Code Duplication Detection**
   - Duplicate code identification
   - Similarity analysis
   - Refactoring suggestions

10. **Error Handling Analysis**
    - Exception handling patterns
    - Error handling completeness
    - Best practices assessment

### Test Client Features
- **Chat Interface**: AI-powered code analysis conversations
- **Example Code Samples**: Pre-filled examples for testing
- **Multi-tabbed Interface**: Organized functionality sections
- **Export Functionality**: Save analysis results

## 🎯 Usage Examples

### Code Complexity Analysis
```python
# Example code for complexity analysis
code = """
def calculate_user_data(user_id, data_type, include_history=False):
    if user_id is None or user_id <= 0:
        raise ValueError('Invalid user_id')
    result = {}
    if include_history:
        result['history'] = get_user_history(user_id)
    return result
"""

# Expected result:
{
  "cyclomatic_complexity": 3,
  "function_count": 1,
  "class_count": 0,
  "complexity_level": "low"
}
```

### Code Style Analysis
```python
# Example code with style issues
code = """
def bad_function(  x,y  ):
    if x>0:
        return x*2
    return 0
"""

# Expected result:
{
  "long_lines": [2, 3],
  "trailing_whitespace": [1, 2],
  "style_issues": ["Long lines found at: [2, 3]", "Trailing whitespace at lines: [1, 2]"]
}
```

### Security Pattern Analysis
```python
# Example vulnerable code
code = """
query = f"SELECT * FROM users WHERE id = {user_id}"
os.system(f"ping {user_input}")
"""

# Expected result:
{
  "vulnerabilities": [
    {
      "type": "SQL Injection",
      "description": "F-string SQL query with variable interpolation",
      "line": 2,
      "severity": "high"
    },
    {
      "type": "Command Injection",
      "description": "os.system with f-string",
      "line": 3,
      "severity": "high"
    }
  ],
  "risk_level": "high"
}
```

## 🔧 Configuration

### Server Configuration
The server uses comprehensive logging and analysis tools:

```python
# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('code_metrics_server.log'),
        logging.StreamHandler()
    ]
)
```

### Test Client Configuration
The test client uses `config.json` for MCP server communication:

```json
{
  "server": {
    "url": "http://127.0.0.1:7862/gradio_api/mcp/sse"
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
        "system_prompt": "You are a helpful AI assistant specialized in code analysis..."
      }
    }
  }
}
```

## 🌐 Interface Features

### Server Interface
- **Multi-function Support**: 10 different analysis functions
- **JSON Output**: Structured analysis results
- **Error Handling**: Comprehensive error management
- **Logging**: Detailed operation logging

### Test Client Interface
- **Chat Interface**: AI-powered code analysis conversations
- **Example Code Samples**: Pre-filled examples for testing
- **Multi-tabbed Design**: Organized functionality sections
- **Export Functionality**: Save analysis results

### Interactive Elements
- **Code Input**: Large text areas for code input
- **Analysis Selection**: Multiple analysis types
- **JSON Outputs**: Structured results display
- **Examples**: Pre-filled code examples

## 📊 API Reference

### Core Analysis Functions

#### 1. Code Complexity Analysis
```python
def calculate_code_complexity(code: str) -> str:
    """
    Calculate cyclomatic complexity and other complexity metrics.

    Args:
        code (str): The source code to analyze

    Returns:
        str: JSON string with complexity metrics
    """
```

#### 2. Code Style Analysis
```python
def analyze_code_style(code: str) -> str:
    """
    Analyze code style and formatting issues.

    Args:
        code (str): The source code to analyze

    Returns:
        str: JSON string with style metrics
    """
```

#### 3. Security Pattern Analysis
```python
def analyze_security_patterns(code: str) -> str:
    """
    Analyze code for security vulnerabilities and patterns.

    Args:
        code (str): The source code to analyze

    Returns:
        str: JSON string with security analysis
    """
```

### Response Formats

#### Complexity Analysis Response
```json
{
  "cyclomatic_complexity": 5,
  "function_count": 3,
  "class_count": 1,
  "complexity_level": "medium"
}
```

#### Style Analysis Response
```json
{
  "long_lines": [15, 23],
  "trailing_whitespace": [8, 12],
  "style_issues": ["Long lines found at: [15, 23]"],
  "recommendations": ["Keep lines under 79 characters", "Remove trailing whitespace"]
}
```

#### Security Analysis Response
```json
{
  "vulnerabilities": [
    {
      "type": "SQL Injection",
      "description": "F-string SQL query",
      "line": 10,
      "severity": "high"
    }
  ],
  "risk_level": "medium",
  "recommendations": ["Use parameterized queries", "Validate inputs"]
}
```

## 🔍 Logging

The server includes comprehensive logging for monitoring and debugging:

### Log File
- **Location**: `code_metrics_server.log`
- **Format**: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- **Level**: INFO

### Log Entries
```
2025-07-21 14:22:05,840 - code_metrics_server - INFO - Starting calculate_code_complexity function
2025-07-21 14:22:05,840 - code_metrics_server - INFO - Input code length: 150 characters
2025-07-21 14:22:05,841 - code_metrics_server - INFO - Complexity analysis completed - Complexity: 5, Functions: 3, Classes: 1
2025-07-21 14:22:05,841 - code_metrics_server - INFO - calculate_code_complexity function completed successfully
```

## 🚨 Troubleshooting

### Common Issues

**1. Port Already in Use**
```bash
# Check if port is in use
lsof -i :7862

# Kill process using the port
kill -9 <PID>
```

**2. Missing Dependencies**
```bash
# Install missing packages
pip install gradio
```

**3. Syntax Errors in Code**
```bash
# Test code syntax
python -m py_compile your_code.py
```

### Error Messages

**"Invalid Python syntax"**
- Check code syntax before analysis
- Verify Python version compatibility
- Use proper indentation

**"Analysis failed"**
- Check input code format
- Verify code is valid Python
- Review error logs for details

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
client = MCPClient({"url": "http://127.0.0.1:7862/gradio_api/mcp/sse"})

# Get available tools
tools = client.get_tools()

# Use code complexity analysis
result = client.call_tool("calculate_code_complexity", {"code": "def test(): pass"})
```

## 📈 Performance

### Processing Speed
- **Small code (< 100 lines)**: ~100-500ms
- **Medium code (100-1000 lines)**: ~500ms-2s
- **Large code (> 1000 lines)**: ~2-10s

### Memory Usage
- **Efficient AST parsing**: Minimal memory overhead
- **Stream-based analysis**: Memory-efficient processing
- **No persistent storage**: Stateless operation

## 🔒 Security

### Input Validation
- All code inputs are validated
- Maximum code size limits
- Safe AST parsing

### Local Processing
- No external API calls for analysis
- Local Python AST processing
- No code transmission to external services

## 🤝 Contributing

### Development Setup
1. Clone the repository
2. Install dependencies: `pip install gradio`
3. Run tests: `python -m pytest tests/`
4. Start development server: `python code_metrics_server.py`

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings for all functions
- Include error handling

### Testing
- Test with various code types
- Verify error handling
- Check edge cases
- Validate output formats

## 📚 Additional Resources

### Documentation
- [Python AST Documentation](https://docs.python.org/3/library/ast.html)
- [Gradio Documentation](https://gradio.app/docs/)
- [MCP Protocol](https://modelcontextprotocol.io/)

### Related Projects
- [Pylint](https://www.pylint.org/)
- [Flake8](https://flake8.pycqa.org/)
- [Black](https://black.readthedocs.io/)

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review error messages carefully
3. Verify configuration settings
4. Test with simple examples first
5. Check server logs for detailed information

---

**Note:** This server is designed for development and testing purposes. For production use, ensure proper security measures and error handling are implemented.
