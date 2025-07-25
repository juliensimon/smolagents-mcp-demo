# MCP Server Implementations

This folder contains different MCP server implementations for providing various services and tools. Each server has its own comprehensive README with detailed documentation.

## 📁 Structure

```
server/
├── basic_server/           # Text sentiment analysis server
│   ├── basic_server.py     # Basic sentiment analysis with built-in interface
│   ├── config.json         # Server configuration
│   ├── README.md           # Comprehensive documentation
│   └── __init__.py         # Package initialization
├── code_metrics_server/    # Advanced code analysis server
│   ├── code_metrics_server.py  # 10 different code analysis functions with built-in interface
│   ├── config.json         # Server configuration
│   ├── README.md           # Comprehensive documentation
│   └── __init__.py         # Package initialization
├── git_server/             # Git operations server
│   ├── git_server.py       # 5 Git operations (status, add, commit, diff, log) with built-in interface
│   ├── config.json         # Server configuration
│   ├── README.md           # Comprehensive documentation
│   └── __init__.py         # Package initialization
├── code_retriever_server/  # File retrieval and analysis server
│   ├── code_retriever_server.py  # 5 file operations with built-in interface
│   ├── config.json         # Server configuration
│   ├── README.md           # Comprehensive documentation
│   └── __init__.py         # Package initialization
├── code_security_server/   # Security vulnerability analysis server
│   ├── code_security_server.py  # 6 security analysis functions with built-in interface
│   ├── config.json         # Server configuration
│   ├── README.md           # Comprehensive documentation
│   └── __init__.py         # Package initialization
└── README.md              # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Required packages: `gradio`, `textblob`, `requests`, `smolagents`
- Git repository (for git server functionality)

### Installation
```bash
# Create virtual environment (recommended)
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

# Install required packages
pip install -r requirements.txt

# Navigate to the server directory
cd server
```

## 📋 Server Overview

### 1. Basic Server (`basic_server/`)
- **Port**: 7860 (Server with built-in interface)
- **Functionality**: Text sentiment analysis using TextBlob
- **Features**: Polarity scoring, subjectivity analysis, batch processing
- **Use Case**: Simple text analysis and sentiment detection

### 2. Code Metrics Server (`code_metrics_server/`)
- **Port**: 7862 (Server with built-in interface)
- **Functionality**: Advanced code analysis and quality assessment
- **Features**: 10 analysis functions (complexity, style, security, performance, etc.)
- **Use Case**: Code review, quality assessment, maintainability analysis

### 3. Git Server (`git_server/`)
- **Port**: 7867 (Server with built-in interface)
- **Functionality**: Git operations and version control management
- **Features**: 5 Git operations (status, add, commit, diff, log)
- **Use Case**: File-specific Git workflow management

### 4. Code Retriever Server (`code_retriever_server/`)
- **Port**: 7866 (Server with built-in interface)
- **Functionality**: File retrieval and analysis from HTTP servers
- **Features**: 5 file operations (validate, retrieve, analyze, search, batch)
- **Use Case**: Remote file analysis, content retrieval, URL validation

### 5. Code Security Server (`code_security_server/`)
- **Port**: 7865 (Server with built-in interface)
- **Functionality**: Security vulnerability analysis and assessment
- **Features**: 6 security analysis functions (SQL injection, command injection, etc.)
- **Use Case**: Security auditing, vulnerability detection, secure coding

## 🎯 Launch Commands

### Individual Servers
```bash
# Basic Server
cd basic_server
python basic_server.py  # Server with built-in interface

# Code Metrics Server
cd code_metrics_server
python code_metrics_server.py  # Server with built-in interface

# Git Server
cd git_server
python git_server.py           # Server with built-in interface

# Code Retriever Server
cd code_retriever_server
python code_retriever_server.py  # Server with built-in interface

# Code Security Server
cd code_security_server
python code_security_server.py # Server with built-in interface
```

### All Servers at Once
```bash
# From project root
python start_all_servers.py
```

## 🔧 Configuration

Each server has its own `config.json` file with:
- **Server URL**: MCP server endpoint
- **Model Configuration**: AI model settings for test clients
- **API Settings**: External service configurations

### Example Configuration
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
        "system_prompt": "You are a helpful AI assistant..."
      }
    }
  }
}
```

## 🌐 Interface Features

### Server Interfaces
- **Gradio Web UI**: User-friendly web interfaces
- **MCP Protocol**: Full Model Context Protocol implementation
- **JSON Responses**: Structured data output
- **Error Handling**: Robust error management
- **Logging**: Comprehensive operation logging

### Test Client Interfaces
- **Multi-tabbed Design**: Organized functionality sections
- **Interactive Examples**: Pre-filled examples for testing
- **Real-time Results**: Instant operation feedback
- **Export Functionality**: Save analysis results
- **AI Integration**: AI-powered analysis and recommendations

## 📊 Port Assignments

| Server | Port | Interface | Status |
|--------|------|-----------|---------|
| Basic Server | 7860 | Built-in Gradio | ✅ Active |
| Code Metrics Server | 7862 | Built-in Gradio | ✅ Active |
| Code Security Server | 7865 | Built-in Gradio | ✅ Active |
| Code Retriever Server | 7866 | Built-in Gradio | ✅ Active |
| Git Server | 7867 | Built-in Gradio | ✅ Active |

## 🔍 Logging

All servers include comprehensive logging:
- **Log Files**: Server-specific log files (e.g., `basic_server.log`)
- **Format**: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- **Level**: INFO
- **Features**: Function call tracking, error logging, performance metrics

## 🔄 Integration

### MCP Protocol Support
All servers implement the Model Context Protocol:
- **Tool Registration**: Automatic tool discovery
- **JSON Communication**: Structured data exchange
- **Error Handling**: Robust error management
- **Logging**: Comprehensive operation logging

### Client Integration
```python
# Example client usage
from smolagents import MCPClient

# Connect to any server
client = MCPClient({"url": "http://127.0.0.1:7862/gradio_api/mcp/sse"})

# Get available tools
tools = client.get_tools()

# Use server functions
result = client.call_tool("function_name", {"param": "value"})
```

## 📚 Documentation

Each server has comprehensive documentation in its `README.md` file:

- **[Basic Server README](basic_server/README.md)** - Text sentiment analysis
- **[Code Metrics Server README](code_metrics_server/README.md)** - Code analysis and quality assessment
- **[Git Server README](git_server/README.md)** - Git operations and version control
- **[Code Retriever Server README](code_retriever_server/README.md)** - File retrieval and analysis
- **[Code Security Server README](code_security_server/README.md)** - Security vulnerability analysis

## 🚨 Troubleshooting

### Common Issues
1. **Port Conflicts**: Check if ports are in use with `lsof -i :PORT`
2. **Missing Dependencies**: Install required packages with `pip install -r requirements.txt`
3. **Git Repository**: Ensure you're in a git repository for git server functionality
4. **Network Issues**: Check connectivity for file retrieval operations
5. **Virtual Environment**: Activate your virtual environment before running servers
6. **Cache Issues**: Clear Python cache with `find . -name "__pycache__" -delete`

### Error Messages
- **"Failed to create interface"**: Check dependencies and configuration
- **"Connection refused"**: Verify server is running on correct port
- **"Git repository not found"**: Initialize git repository with `git init`

## 🤝 Contributing

### Development Setup
1. Clone the repository
2. Install dependencies: `pip install gradio textblob requests smolagents`
3. Navigate to specific server directory
4. Start development server

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings for all functions
- Include error handling

### Testing
- Test with various input types
- Verify error handling
- Check edge cases
- Validate output formats

## 📞 Support

For issues and questions:
1. Check individual server README files
2. Review error messages carefully
3. Verify configuration settings
4. Test with simple examples first
5. Check server logs for detailed information

---

**Note:** These servers are designed for development and testing purposes. For production use, ensure proper security measures and error handling are implemented.
