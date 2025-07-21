# Code Retriever Server - File Retrieval and Analysis

A comprehensive MCP server implementation for retrieving and analyzing files from HTTP servers. This server provides URL validation, file content retrieval, content analysis, and search capabilities for various file types.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Required packages: `gradio`, `requests`, `urllib`

### Installation
```bash
# Install required packages
pip install gradio requests

# Navigate to the code retriever server directory
cd server/code_retriever_server
```

### Launch Server
```bash
python code_retriever_server.py
```
**Server Port:** 7866
**Access:** http://localhost:7866

## 📋 Features

### Server Functionality
The server provides 5 comprehensive file retrieval and analysis functions:

1. **URL Validation**
   - Validate URL accessibility
   - Check HTTP status codes
   - Extract file metadata
   - Content type detection

2. **File Content Retrieval**
   - Download file content from URLs
   - Metadata extraction
   - Content hashing
   - Download timing

3. **Content Analysis**
   - File type detection
   - Line and word counting
   - Code structure analysis
   - Readability metrics

4. **Content Search**
   - Text search within files
   - Case-sensitive/insensitive search
   - Search result highlighting
   - Match counting

5. **Batch Retrieval**
   - Multiple URL processing
   - Parallel downloads
   - Summary statistics
   - Error handling



## 🎯 Usage Examples

### URL Validation
```python
# Validate a GitHub file URL
url = "https://raw.githubusercontent.com/github/gitignore/master/Python.gitignore"

# Expected result:
{
  "valid": true,
  "url": "https://raw.githubusercontent.com/github/gitignore/master/Python.gitignore",
  "content_type": "text/plain; charset=utf-8",
  "content_length": "1234",
  "last_modified": "Mon, 21 Jul 2025 10:00:00 GMT",
  "file_extension": ".gitignore",
  "status_code": 200
}
```

### File Content Retrieval
```python
# Retrieve a Python file
url = "https://raw.githubusercontent.com/python/cpython/main/Lib/os.py"
include_metadata = true

# Expected result:
{
  "success": true,
  "url": "https://raw.githubusercontent.com/python/cpython/main/Lib/os.py",
  "content": "# OS routines for NT or Posix depending on what system we're on...",
  "content_length": 45678,
  "content_hash": "a1b2c3d4e5f6...",
  "download_time": 1.234,
  "encoding": "utf-8",
  "content_type": "text/plain; charset=utf-8",
  "last_modified": "Mon, 21 Jul 2025 10:00:00 GMT"
}
```

### Content Analysis
```python
# Analyze a Python file
content = """
def hello_world():
    print("Hello, World!")

class Example:
    def __init__(self):
        self.name = "example"
"""

file_type = "auto"

# Expected result:
{
  "file_size": 89,
  "line_count": 8,
  "word_count": 12,
  "character_count": 89,
  "non_whitespace_count": 67,
  "file_type_detected": "python",
  "function_count": 2,
  "class_count": 1,
  "avg_words_per_line": 1.5,
  "avg_chars_per_word": 5.58
}
```

### Content Search
```python
# Search for "def" in Python code
content = """
def function1():
    pass

def function2():
    pass
"""

search_term = "def"
case_sensitive = false

# Expected result:
{
  "search_term": "def",
  "case_sensitive": false,
  "matches": [
    {
      "line": 2,
      "position": 0,
      "context": "def function1():"
    },
    {
      "line": 5,
      "position": 0,
      "context": "def function2():"
    }
  ],
  "total_matches": 2,
  "search_time": 0.001
}
```

## 🔧 Configuration

### Server Configuration
The server uses comprehensive logging and HTTP handling:

```python
# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('code_retriever_server.log'),
        logging.StreamHandler()
    ]
)
```



## 🌐 Interface Features

### Server Interface
- **Multi-function Support**: 5 different file operations
- **JSON Output**: Structured file operation results
- **Error Handling**: Comprehensive error management
- **Logging**: Detailed operation logging



### Interactive Elements
- **URL Input**: Text inputs for URLs
- **Content Input**: Large text areas for content
- **Search Input**: Text inputs for search terms
- **Checkboxes**: Toggle options and features
- **JSON Outputs**: Structured results display
- **Examples**: Pre-filled examples for quick testing

## 📊 API Reference

### Core File Functions

#### 1. URL Validation
```python
def validate_url(url: str) -> Dict[str, Any]:
    """
    Validate if the provided URL is accessible and returns file information.

    Args:
        url (str): The URL to validate

    Returns:
        dict: JSON string with validation results
    """
```

#### 2. File Content Retrieval
```python
def retrieve_file_content(url: str, include_metadata: bool = True) -> str:
    """
    Retrieve the content of a file from an HTTP server.

    Args:
        url (str): The URL of the file to retrieve
        include_metadata (bool): Whether to include metadata in the response

    Returns:
        str: JSON string with file content and metadata
    """
```

#### 3. Content Analysis
```python
def analyze_file_content(content: str, file_type: str = "auto") -> str:
    """
    Analyze the content of a retrieved file.

    Args:
        content (str): The file content to analyze
        file_type (str): The type of file (auto, text, code, json, xml, etc.)

    Returns:
        str: JSON string with analysis results
    """
```

#### 4. Content Search
```python
def search_file_content(content: str, search_term: str, case_sensitive: bool = False) -> str:
    """
    Search for specific terms within file content.

    Args:
        content (str): The file content to search
        search_term (str): The term to search for
        case_sensitive (bool): Whether the search should be case sensitive

    Returns:
        str: JSON string with search results
    """
```

### Response Formats

#### URL Validation Response
```json
{
  "valid": true,
  "url": "https://example.com/file.py",
  "content_type": "text/plain; charset=utf-8",
  "content_length": "1234",
  "last_modified": "Mon, 21 Jul 2025 10:00:00 GMT",
  "file_extension": ".py",
  "status_code": 200
}
```

#### File Retrieval Response
```json
{
  "success": true,
  "url": "https://example.com/file.py",
  "content": "# File content here...",
  "content_length": 1234,
  "content_hash": "a1b2c3d4e5f6...",
  "download_time": 1.234,
  "encoding": "utf-8",
  "content_type": "text/plain; charset=utf-8"
}
```

#### Content Analysis Response
```json
{
  "file_size": 1234,
  "line_count": 50,
  "word_count": 200,
  "character_count": 1234,
  "file_type_detected": "python",
  "function_count": 5,
  "class_count": 2,
  "avg_words_per_line": 4.0,
  "avg_chars_per_word": 6.17
}
```

## 🔍 Logging

The server includes comprehensive logging for monitoring and debugging:

### Log File
- **Location**: `code_retriever_server.log`
- **Format**: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- **Level**: INFO

### Log Entries
```
2025-07-21 14:22:05,840 - code_retriever_server - INFO - Starting validate_url function
2025-07-21 14:22:05,840 - code_retriever_server - INFO - Input url: https://example.com/file.py
2025-07-21 14:22:05,841 - code_retriever_server - INFO - URL validation completed - Valid: True, Status: 200
2025-07-21 14:22:05,841 - code_retriever_server - INFO - validate_url function completed successfully
```

## 🚨 Troubleshooting

### Common Issues

**1. Port Already in Use**
```bash
# Check if port is in use
lsof -i :7866

# Kill process using the port
kill -9 <PID>
```

**2. Network Connectivity Issues**
```bash
# Test network connectivity
curl -I https://example.com

# Check DNS resolution
nslookup example.com
```

**3. URL Access Issues**
```bash
# Test URL accessibility
curl -L https://example.com/file.py

# Check HTTP status
curl -I https://example.com/file.py
```

### Error Messages

**"Request timeout"**
- Check network connectivity
- Verify URL is accessible
- Try with different timeout settings

**"Connection error"**
- Check internet connection
- Verify URL format
- Test with different URLs

**"HTTP 404: Not Found"**
- Verify URL is correct
- Check if file exists
- Try different file paths

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
client = MCPClient({"url": "http://127.0.0.1:7866/gradio_api/mcp/sse"})

# Get available tools
tools = client.get_tools()

# Use URL validation
result = client.call_tool("validate_url", {"url": "https://example.com/file.py"})
```

## 📈 Performance

### Processing Speed
- **URL validation**: ~100-500ms
- **File retrieval**: ~500ms-10s (depends on file size)
- **Content analysis**: ~50-200ms
- **Content search**: ~10-100ms

### Memory Usage
- **Efficient HTTP handling**: Minimal memory overhead
- **Stream-based processing**: Memory-efficient downloads
- **No persistent storage**: Stateless operation

## 🔒 Security

### Input Validation
- All URLs are validated
- Content size limits
- Safe HTTP requests

### Network Security
- HTTPS support
- Request timeout limits
- User-Agent headers
- No sensitive data transmission

## 🤝 Contributing

### Development Setup
1. Clone the repository
2. Install dependencies: `pip install gradio requests`
3. Run tests: `python -m pytest tests/`
4. Start development server: `python code_retriever_server.py`

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings for all functions
- Include error handling

### Testing
- Test with various URL types
- Verify error handling
- Check edge cases
- Validate output formats

## 📚 Additional Resources

### Documentation
- [Requests Documentation](https://requests.readthedocs.io/)
- [Gradio Documentation](https://gradio.app/docs/)
- [MCP Protocol](https://modelcontextprotocol.io/)

### Related Projects
- [Requests](https://requests.readthedocs.io/)
- [urllib3](https://urllib3.readthedocs.io/)
- [aiohttp](https://aiohttp.readthedocs.io/)

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review error messages carefully
3. Verify network connectivity
4. Test with simple examples first
5. Check server logs for detailed information

---

**Note:** This server is designed for development and testing purposes. For production use, ensure proper security measures and error handling are implemented.
