# 🤖 MCP Multi-Agent Demo

> **A comprehensive demonstration of Model Context Protocol (MCP) applications built with open source tools**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## What is this?

This is a **comprehensive demo** showing how to build **Model Context Protocol (MCP) applications** using open source tools. It demonstrates:

- 🏗️ **MCP Server Development** - How to create specialized MCP servers
- 🤖 **Multi-Agent Systems** - Building intelligent agent teams with Smolagents
- 🔧 **Tool Integration** - Connecting agents to external APIs and services
- 📊 **Real-world Use Cases** - Code analysis, security scanning, file operations
- 🧪 **Testing & Validation** - Comprehensive testing strategies for MCP applications

**Perfect for developers** who want to:
- Learn MCP fundamentals
- Build their own MCP servers
- Create multi-agent applications
- Understand MCP best practices

## 🚀 Progressive Quickstart

Start simple and work your way up to advanced multi-agent systems:

### Step 1: Basic Client (1 Tool, 1 Agent)
**Perfect for understanding MCP fundamentals**

```bash
# Setup environment
git clone https://github.com/juliensimon/smolagents-mcp-demo.git
cd smolagents-mcp-demo
export TOGETHER_API_KEY="your-api-key-here"
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
pip install -r requirements.txt

# Start one server
python server/basic_server/basic_server.py

# In another terminal, run basic client
python client/basic_client/client.py
```

**What you'll learn:**
- How MCP clients connect to servers
- Basic tool usage with AI agents
- Simple text analysis capabilities

### Step 2: Single Agent Client (Many Tools, 1 Agent)
**Learn to work with multiple MCP servers**

```bash
# Start all servers
python start_all_servers.py

# Run the unified client
python client/code_client/client.py
```

**What you'll learn:**
- Connecting to multiple MCP servers
- Tool discovery and routing
- Unified interface for different capabilities
- Server status monitoring

### Step 3: Multi-Agent Client (Many Tools, Many Agents)
**Experience advanced multi-agent coordination**

```bash
# Start all servers (if not already running)
python start_all_servers.py

# Launch the multi-agent system
python client/multi_agent_client/client.py
```

**What you'll learn:**
- Agent specialization and delegation
- Intelligent task routing
- Multi-agent coordination patterns
- Advanced MCP application architecture

## 🎯 What You'll Learn

### MCP Server Development
- **Server Architecture** - How to structure MCP servers
- **Tool Implementation** - Creating custom tools and functions
- **Error Handling** - Robust error management in MCP servers
- **Configuration** - Centralized configuration management
- **Testing** - Comprehensive testing strategies

### Multi-Agent Systems
- **Agent Specialization** - Different agents for different tasks
- **Task Delegation** - Intelligent routing between agents
- **Tool Coordination** - Agents using MCP servers as tools
- **Conversation Management** - Multi-turn agent interactions

### Available MCP Servers (Learning Examples)

| Server | Purpose | What You'll Learn |
|--------|---------|-------------------|
| **Code Metrics** | Code quality analysis | Implementing analysis tools, metrics calculation |
| **Code Security** | Vulnerability detection | Security scanning, pattern recognition |
| **Code Retrieval** | File operations | HTTP handling, file processing, error management |
| **Git Server** | Repository management | Git operations, version control integration |
| **Basic Server** | Text processing | Simple tool implementation, text analysis |

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Multi-Agent Client                       │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────┐          │
│  │ Code Agent  │ │Research Agent│ │Manager Agent │          │
│  │(coder-large)│ │(coder-large) │ │(coder-large) │          │
│  └─────────────┘ └──────────────┘ └──────────────┘          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────┐
│                    MCP Servers                             │
│  ┌─────────────┐ ┌─────────────┐ ┌──────────────┐          │
│  │ Code Metrics│ │Code Security│ │Code Retrieval│          │
│  │   (7862)    │ │   (7865)    │ │   (7866)     │          │
│  └─────────────┘ └─────────────┘ └──────────────┘          │
│  ┌─────────────┐ ┌─────────────┐                           │
│  │ Git Server  │ │Basic Server │                           │
│  │   (7867)    │ │   (7860)    │                           │
│  └─────────────┘ └─────────────┘                           │
└────────────────────────────────────────────────────────────┘
```

## 🧪 Try It Out

### Quick Examples

**Code Analysis:**
```
"Analyze the complexity of this Python function and suggest improvements"
```

**Security Scan:**
```
"Check this code for potential security vulnerabilities"
```

**File Operations:**
```
"Download and analyze the README from this GitHub repository"
```

**Git Operations:**
```
"What's the current status of this repository and what changes are pending?"
```

## 🔧 Development & Customization

### Building Your Own MCP Server

1. **Study the examples** in `server/` directory
2. **Create your server:**
   ```bash
   mkdir server/my_new_server
   cp server/basic_server/basic_server.py server/my_new_server/my_new_server.py
   ```

3. **Add to configuration:**
   ```json
   "my_new_server": {
     "name": "My New Server",
     "port": 7868,
     "url": "http://127.0.0.1:7868/gradio_api/mcp/sse",
     "description": "My custom functionality",
     "path": "server/my_new_server/my_new_server.py"
   }
   ```

4. **Implement your tools** following the MCP specification

### Testing Your MCP Application

```bash
# Quick validation
python run_tests.py validate

# Test all functionality
python run_tests.py all

# Health check servers
python run_tests.py health
```

## 📚 Learning Resources

### MCP Fundamentals
- **MCP Specification**: [Model Context Protocol](https://modelcontextprotocol.io/)
- **MCP Tools**: Understanding tool definitions and implementations
- **Server Communication**: How clients and servers interact

### Multi-Agent Development
- **Smolagents**: Multi-agent framework documentation
- **Agent Patterns**: Specialization, delegation, coordination
- **Tool Integration**: Connecting agents to external services

### Advanced Topics
- **Configuration Management**: See [CONFIGURATION.md](CONFIGURATION.md)
- **Testing Strategies**: Comprehensive test suite examples
- **Error Handling**: Robust error management patterns
- **Performance Optimization**: Scaling MCP applications

## 🛠️ Development Tools

### Code Quality
```bash
# Install pre-commit hooks
./setup_precommit.sh

# Run quality checks
pre-commit run --all-files
```

### API Documentation
Each server provides interactive docs:
- **Basic Server**: http://127.0.0.1:7860
- **Code Metrics**: http://127.0.0.1:7862
- **Code Security**: http://127.0.0.1:7865
- **Code Retrieval**: http://127.0.0.1:7866
- **Git Server**: http://127.0.0.1:7867

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

**Built with ❤️ for the AI community**
