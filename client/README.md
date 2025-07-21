# MCP Client Implementations

This folder contains different MCP client implementations for connecting to and using MCP servers.

## Structure

```
client/
├── basic_client/          # Basic client with AI integration
│   ├── client.py          # Gradio interface with AI agent
│   ├── config_loader.py   # Configuration utilities
│   ├── config.json        # Configuration file
│   ├── __init__.py        # Package initialization
│   └── README.md          # Basic client documentation
├── code_client/           # Multi-server client implementation
│   ├── client.py          # Unified client for multiple servers
│   ├── config_loader.py   # Configuration utilities
│   ├── config.json        # Configuration file
│   ├── __init__.py        # Package initialization
│   └── README.md          # Multi-server client documentation
├── multi_agent_client/    # Multi-agent system client
│   ├── client.py          # Multi-agent coordination system
│   ├── demo_interface.py  # Demo interface for testing
│   ├── test_multi_agent.py # Multi-agent test suite
│   ├── __init__.py        # Package initialization
│   └── README.md          # Multi-agent client documentation
└── README.md             # This file
```

## Client Types

### Basic Client (`basic_client/`)
- Full-featured client with Gradio web interface
- AI agent integration for intelligent tool usage
- Support for multiple AI models
- Interactive chat interface

### Code Client (`code_client/`)
- Multi-server client that connects to all available MCP servers
- Unified interface for code analysis, security scanning, and git operations
- Intelligent routing to appropriate servers
- Server status monitoring

### Multi-Agent Client (`multi_agent_client/`)
- Advanced multi-agent system with specialized agents
- Code Agent (coder-large) for code analysis and security
- Research Agent (AFM-4.5B) for file retrieval and git operations
- Manager Agent for intelligent task delegation
- Web Search Agent for additional research capabilities

## Quick Start

### Basic Client
```bash
cd client/basic_client
export TOGETHER_API_KEY="your_api_key_here"
python client.py
```

### Code Client
```bash
cd client/code_client
export TOGETHER_API_KEY="your_api_key_here"
python client.py
```

### Multi-Agent Client
```bash
cd client/multi_agent_client
export TOGETHER_API_KEY="your_api_key_here"
python client.py
```

## Configuration

Each client folder has its own `config.json` file that can be customized independently:

- **Server URL**: Configure which MCP server to connect to
- **Model Settings**: AI model configuration for advanced client
- **API Settings**: API endpoints and authentication

## Clean Structure

The client directory has been reorganized for better separation of concerns. Each client type has its own folder with all necessary files, making it easy to maintain and extend individual client implementations.
