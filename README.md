# 🤖 Smolagents MCP Demo

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports](https://img.shields.io/badge/imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Linting](https://img.shields.io/badge/linting-flake8-yellowgreen)](https://flake8.pycqa.org/)
[![Type Checking](https://img.shields.io/badge/type%20checking-mypy-blue)](https://mypy-lang.org/)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Tests](https://img.shields.io/badge/tests-unittest-brightgreen)](https://docs.python.org/3/library/unittest.html)

> **A comprehensive demonstration of Model Context Protocol (MCP) servers and clients, showcasing AI-powered tools and multi-agent systems for code analysis, security scanning, and intelligent automation.**

## 🌟 Features

- **🤖 Multi-Agent System**: Intelligent agents with specialized capabilities
- **🔍 Code Analysis**: Metrics, complexity, and quality assessment
- **🛡️ Security Scanning**: Vulnerability detection and security auditing
- **📁 File Retrieval**: HTTP file processing, content analysis, and secure file operations
- **📊 Git Operations**: Repository management and version control
- **💬 Sentiment Analysis**: Text emotion and tone analysis
- **🎯 Unified Interface**: Single platform for all AI-powered tools
- **⚙️ Configurable**: Centralized configuration management
- **🧪 Comprehensive Testing**: Full test suite with multiple scenarios

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Multi-Agent Client                       │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────┐          │
│  │ Code Agent  │ │Research Agent│ │Manager Agent │          │
│  │(coder-large)│ │(AFM-4.5B)    │ │(AFM-4.5B)    │          │
│  └─────────────┘ └──────────────┘ └──────────────┘          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────┐
│                    MCP Servers                             │
│  ┌─────────────┐ ┌─────────────┐ ┌──────────────           │
│  │ Code Metrics│ │Code Security│ │Code Retrieval│          │
│  │   (7862)    │ │   (7865)    │ │   (7866)     │          │
│  └─────────────┘ └─────────────┘ └──────────────┘          │
│  ┌─────────────┐ ┌─────────────┐                           │
│  │ Git Server  │ │Basic Server │                           │
│  │   (7867)    │ │   (7860)    │                           │
│  └─────────────┘ └─────────────┘                           │
└────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Git**
- **Together AI API Key**

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/juliensimon/smolagents-mcp-demo.git
   cd smolagents-mcp-demo
   ```

2. **Set up environment**:
   ```bash
   export TOGETHER_API_KEY="your-api-key-here"
   pip install -r requirements.txt
   ```

3. **Start all servers**:
   ```bash
   python start_all_servers.py
   ```

4. **Launch the multi-agent client** (recommended):
   ```bash
   python client/multi_agent_client/client.py
   ```

## 🎯 Multi-Agent System

### Specialized Agents

| Agent | Model | Specialization | Capabilities |
|-------|-------|----------------|--------------|
| **Code Agent** | [coder-large](https://api.together.ai/models/arcee-ai/coder-large) | Code Analysis | Metrics, complexity, style analysis |
| **Research Agent** | [AFM-4.5B-Preview](https://api.together.ai/models/arcee-ai/AFM-4.5B-Preview) | Research & Retrieval | File retrieval, git ops, web search |
| **Manager Agent** | [AFM-4.5B-Preview](https://api.together.ai/models/arcee-ai/AFM-4.5B-Preview) | Task Delegation | Intelligent routing, workflow management |

### Intelligent Workflow

1. **Task Analysis**: Manager agent analyzes user requests
2. **Agent Selection**: Automatically routes to appropriate specialist
3. **Execution**: Specialized agent performs the task
4. **Integration**: Results are combined and presented

## 🔧 Available Servers

| Server | Port | Purpose | Key Features |
|--------|------|---------|--------------|
| **Basic Server** | 7860 | Text Analysis | Sentiment analysis, emotion detection |
| **Code Metrics** | 7862 | Code Quality | Complexity, maintainability, style metrics |
| **Code Security** | 7865 | Security Audit | Vulnerability detection, security scanning |
| **Code Retrieval** | 7866 | File Processing | HTTP retrieval, content analysis |
| **Git Server** | 7867 | Version Control | Repository operations, commit analysis |

## 📊 Capabilities

### 🔍 Code Analysis
- **Complexity Metrics**: Cyclomatic complexity, cognitive complexity
- **Style Analysis**: PEP 8 compliance, naming conventions
- **Maintainability**: Maintainability index, technical debt assessment
- **Documentation**: Docstring coverage, comment analysis

### 🛡️ Security Scanning
- **SQL Injection**: Detection of vulnerable database queries
- **Command Injection**: Identification of unsafe system calls
- **Hardcoded Secrets**: Detection of exposed credentials
- **Path Traversal**: Identification of directory traversal vulnerabilities
- **XSS Detection**: Cross-site scripting vulnerability analysis

### 📁 File Operations
- **HTTP Retrieval**: Secure file downloading and validation with error handling
- **Content Analysis**: File type detection, metadata extraction, and content parsing
- **Batch Processing**: Multiple file processing with progress tracking
- **Search Integration**: Content search, filtering, and intelligent file discovery
- **Security Validation**: URL validation, content type verification, and safe file handling

### 📊 Git Integration
- **Repository Status**: File status and change tracking
- **Commit Operations**: Staging, committing, and diff analysis
- **History Analysis**: Commit history and change patterns
- **Branch Management**: Branch operations and comparison

## 🧪 Testing

The project includes a comprehensive test suite with multiple scenarios and categories, organized into offline and online tests:

### Quick Start
```bash
# Run from root directory (recommended)
python run_tests.py validate

# List available test categories
python run_tests.py list

# List available test scenarios
python run_tests.py list-scenarios
```

### Test Organization

The test suite is organized into two categories:

**Offline Tests** (CI/CD Safe):
- Configuration and environment validation
- File structure and import checks
- No external dependencies required

**Online Tests** (Require Live Servers):
- Real MCP server integration
- Server functionality testing
- External endpoint validation

### Test Categories
```bash
# Quick validation (environment & configuration)
python run_tests.py quick

# Health checks (server connectivity)
python run_tests.py health

# Core functionality (integration & scenarios)
python run_tests.py core

# All server functionality tests
python run_tests.py functionality

# Complete test suite
python run_tests.py all
```

### Test Scenarios
```bash
# Smoke tests (basic functionality)
python run_tests.py smoke

# Integration tests (full server integration)
python run_tests.py integration

# Performance tests (stress testing)
python run_tests.py performance

# Security tests (vulnerability scanning)
python run_tests.py security

# Full test suite (all categories)
python run_tests.py full
```

### Individual Categories
```bash
# Specific test categories
python run_tests.py environment
python run_tests.py configuration
python run_tests.py basic_functionality
python run_tests.py code_metrics_functionality
python run_tests.py code_security_functionality
python run_tests.py code_retrieval_functionality
python run_tests.py git_functionality
```

### Dedicated Test Runners
```bash
# Offline tests only (CI/CD safe)
python tests/run_offline_tests.py all

# Online tests only (requires servers)
python tests/run_online_tests.py all

# User-friendly wrapper
python tests/run_test_suite.py all
```

### Advanced Options
```bash
# Verbose output
python run_tests.py all --verbose

# Generate detailed report
python run_tests.py all --report

# Run from tests directory (alternative)
python tests/run_tests.py all
```

## ⚙️ Configuration

The project uses a **unified configuration system** (`config.json`):

```json
{
  "servers": {
    "basic": {"port": 7860, "name": "Basic Server"},
    "code_metrics": {"port": 7862, "name": "Code Metrics"},
    "code_security": {"port": 7865, "name": "Code Security"},
    "code_retrieval": {"port": 7866, "name": "Code Retrieval"},
    "git": {"port": 7867, "name": "Git Server"}
  },
  "model": {
    "default": "togethercomputer/llama-2-70b-chat",
    "api_base": "https://api.together.xyz/v1"
  }
}
```

## 🛠️ Development

### Code Quality

```bash
# Install pre-commit hooks
./setup_precommit.sh

# Run quality checks
pre-commit run --all-files
```

### Adding New Servers

1. **Add configuration** to `config.json`
2. **Implement server** in `server/new_server/`
3. **Add tests** to test suite
4. **Update documentation**

## 📚 API Documentation

Each server provides interactive API documentation:

- **Basic Server**: http://127.0.0.1:7860
- **Code Metrics**: http://127.0.0.1:7862
- **Code Security**: http://127.0.0.1:7865
- **Code Retrieval**: http://127.0.0.1:7866
- **Git Server**: http://127.0.0.1:7867

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Test** thoroughly
5. **Submit** a pull request

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [CONFIGURATION.md](CONFIGURATION.md)
- **Issues**: [GitHub Issues](https://github.com/juliensimon/smolagents-mcp-demo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/juliensimon/smolagents-mcp-demo/discussions)

## 🙏 Acknowledgments

- **Smolagents**: Multi-agent framework
- **Together AI**: Model hosting and inference
- **Gradio**: Web interface framework
- **MCP**: Model Context Protocol specification

---

**Made with ❤️ for the AI community**
