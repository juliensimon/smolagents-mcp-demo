# MCP Client Implementations

This folder contains different MCP client implementations for connecting to and using MCP servers.

## Structure

```
client/
├── list_tool/             # List tool client implementation
│   ├── basic_client.py    # List tool client
│   ├── config_loader.py   # Configuration utilities
│   ├── config.json        # Configuration file
│   ├── __init__.py        # Package initialization
│   └── README.md          # List tool client documentation
├── basic_client/          # Basic client with AI integration
│   ├── client.py          # Gradio interface with AI agent
│   ├── config_loader.py   # Configuration utilities
│   ├── config.json        # Configuration file
│   ├── __init__.py        # Package initialization
│   └── README.md          # Basic client documentation
└── README.md             # This file
```

## Client Types

### List Tool Client (`list_tool/`)
- Simple implementation that connects to MCP server
- Lists all available tools
- Minimal dependencies
- Good for testing and debugging

### Basic Client (`basic_client/`)
- Full-featured client with Gradio web interface
- AI agent integration for intelligent tool usage
- Support for multiple AI models
- Interactive chat interface

## Quick Start

### List Tool Client
```bash
cd client/list_tool
python basic_client.py
```

### Basic Client
```bash
cd client/basic_client
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
