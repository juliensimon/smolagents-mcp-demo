# Unified Configuration System

This document describes the unified configuration system for the MCP Demo project.

## Overview

The MCP Demo project now uses a single, centralized configuration file (`config.json`) that is shared across all components:
- **Servers**: All MCP servers read their port numbers and settings from this file
- **Clients**: All client applications use the same configuration
- **Tests**: All test suites use the unified configuration
- **Server Manager**: The server startup script uses the unified configuration

## Configuration File Structure

The main configuration file is located at `config.json` in the project root:

```json
{
  "servers": {
    "basic_server": {
      "name": "Basic Server",
      "port": 7860,
      "url": "http://127.0.0.1:7860/gradio_api/mcp/sse",
      "description": "Basic text sentiment analysis",
      "path": "server/basic_server/basic_server.py"
    },
    "code_metrics": {
      "name": "Code Metrics Server",
      "port": 7862,
      "url": "http://127.0.0.1:7862/gradio_api/mcp/sse",
      "description": "Code analysis and metrics",
      "path": "server/code_metrics_server/code_metrics_server.py"
    },
    "code_security": {
      "name": "Code Security Server",
      "port": 7865,
      "url": "http://127.0.0.1:7865/gradio_api/mcp/sse",
      "description": "Security vulnerability detection",
      "path": "server/code_security_server/code_security_server.py"
    },
    "code_retrieval": {
      "name": "Code Retrieval Server",
      "port": 7866,
      "url": "http://127.0.0.1:7866/gradio_api/mcp/sse",
      "description": "Code retrieval",
      "path": "server/code_retriever_server/code_retriever_server.py"
    },
    "git_repo_analysis": {
      "name": "Git Repo Analysis Server",
      "port": 7867,
      "url": "http://127.0.0.1:7867/gradio_api/mcp/sse",
      "description": "Git repository analysis",
      "path": "server/git_server/git_server.py"
    }
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
        "system_prompt": "You are a helpful AI assistant specialized in using tools and writing code. You have access to multiple MCP servers."
      }
    }
  },
  "client": {
    "gradio": {
      "server_name": "127.0.0.1",
      "server_port": 7864,
      "share": false,
      "show_error": true,
      "theme": "default"
    }
  },
  "testing": {
    "timeout": 30,
    "retry_attempts": 3,
    "health_check_interval": 5,
    "startup_wait_time": 3
  },
  "logging": {
    "level": "INFO",
    "file": "mcp_servers.log",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  }
}
```

## Configuration Loader

The `config_loader.py` module provides a unified interface for accessing configuration:

### Basic Usage

```python
from config_loader import get_config_loader

# Get the configuration loader
config_loader = get_config_loader()

# Get all servers
servers = config_loader.get_servers()

# Get a specific server's port
port = config_loader.get_server_port("code_metrics")

# Get model parameters
model_params = config_loader.get_model_params()
```

### Convenience Functions

```python
from config_loader import get_server_port, get_server_url, get_model_params

# Direct access to common configuration values
port = get_server_port("code_metrics")
url = get_server_url("code_metrics")
params = get_model_params()
```

## Server Configuration

Each server is configured with:
- **name**: Human-readable server name
- **port**: Port number for the server
- **url**: Full MCP server URL
- **description**: Brief description of server functionality
- **path**: Path to the server's main Python file

### Server Ports

| Server | Port | Description |
|--------|------|-------------|
| Basic Server | 7860 | Text sentiment analysis |
| Code Metrics | 7862 | Code analysis and metrics |
| Code Security | 7865 | Security vulnerability detection |
| Code Retrieval | 7866 | HTTP file retrieval and analysis |
| Git Repo Analysis | 7867 | Git repository operations |

## Model Configuration

The model configuration includes:
- **default**: Default model to use
- **api_base**: API base URL for the model provider
- **configs**: Model-specific parameters

## Client Configuration

Client configuration includes Gradio interface settings:
- **server_name**: Hostname for the client interface
- **server_port**: Port for the client interface
- **share**: Whether to create public links
- **show_error**: Whether to show errors in the interface
- **theme**: Gradio theme to use

## Testing Configuration

Testing configuration includes:
- **timeout**: Request timeout in seconds
- **retry_attempts**: Number of retry attempts for failed requests
- **health_check_interval**: Interval for health checks
- **startup_wait_time**: Time to wait for servers to start

## Logging Configuration

Logging configuration includes:
- **level**: Logging level (DEBUG, INFO, WARNING, ERROR)
- **file**: Log file path
- **format**: Log message format

## Usage in Components

### Servers

All servers now use the unified configuration:

```python
from config_loader import get_config_loader

config_loader = get_config_loader()
server_config = config_loader.get_server_config("code_metrics")
port = server_config["port"]

# Launch server on configured port
demo.launch(server_port=port, mcp_server=True)
```

### Clients

Clients use the unified configuration through a wrapper:

```python
from client.code_client.config_loader import load_config

config = load_config()
servers = config["servers"]
model_config = config["model"]
```

### Tests

Tests use the unified configuration directly:

```python
from config_loader import get_config_loader

config_loader = get_config_loader()
servers = config_loader.get_servers()
```

## Benefits

1. **Single Source of Truth**: All configuration is centralized in one file
2. **Consistency**: All components use the same configuration
3. **Maintainability**: Changes to configuration only need to be made in one place
4. **Validation**: Configuration is validated for correctness
5. **Flexibility**: Easy to add new servers or modify existing ones

## Validation

The configuration system includes validation to ensure:
- All required sections are present
- Server configurations are complete
- Port numbers are valid integers
- URLs are properly formatted
- Model configurations are complete

Run validation with:
```bash
python config_loader.py
```

## Adding New Servers

To add a new server:

1. Add the server configuration to `config.json`:
```json
"new_server": {
  "name": "New Server",
  "port": 7868,
  "url": "http://127.0.0.1:7868/gradio_api/mcp/sse",
  "description": "New server functionality",
  "path": "server/new_server/new_server.py"
}
```

2. Update the server's Python file to use the unified configuration
3. The server will automatically be included in all management scripts

## Troubleshooting

### Configuration Not Found
- Ensure `config.json` exists in the project root
- Check file permissions

### Import Errors
- Ensure the project root is in the Python path
- Check that `config_loader.py` is accessible

### Port Conflicts
- Verify that port numbers are unique across all servers
- Check that ports are not already in use by other applications

### Validation Failures
- Check that all required fields are present
- Verify URL formats are correct
- Ensure port numbers are integers
