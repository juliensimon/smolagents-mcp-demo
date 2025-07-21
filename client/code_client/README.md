# Multi-Server MCP Client

A unified client that connects to multiple MCP (Model Context Protocol) servers and provides an intelligent interface for code analysis, security scanning, git operations, and file retrieval.

## Features

- **Multi-Server Support**: Connects to all available MCP servers
- **Unified Interface**: Single chat interface for all operations
- **Intelligent Routing**: Automatically routes requests to appropriate servers
- **Server Status Monitoring**: Check connection status of all servers
- **Tool Discovery**: Automatically discovers and uses available tools

## Connected Servers

1. **Basic Server** (Port 7860)
   - Text sentiment analysis
   - Emotion detection and text processing

2. **Code Metrics Server** (Port 7862)
   - Code complexity analysis
   - Code quality metrics
   - Performance analysis

3. **Code Security Server** (Port 7865)
   - Security vulnerability detection
   - Code security analysis
   - Best practices checking

4. **Code Retrieval Server** (Port 7866)
   - HTTP file retrieval and analysis
   - URL validation and content fetching

5. **Git Server** (Port 7867)
   - Git operations on local files
   - Repository status and history
   - File tracking and changes

## Configuration

The client uses `config.json` to configure:
- Server URLs and descriptions
- Model settings (Together AI)
- Gradio interface settings

### Environment Variables

- `TOGETHER_API_KEY`: Your Together AI API key
- `TOGETHER_MODEL`: Model to use (default: arcee-ai/AFM-4.5B-Preview)

## Usage

1. **Start the servers**:
   ```bash
   python start_all_servers.py
   ```

2. **Run the client**:
   ```bash
   python client.py
   ```

3. **Access the interface**:
   - Open http://127.0.0.1:7864 in your browser
   - Use the chat interface to interact with all servers

## Example Requests

- **Code Analysis**: "Analyze the complexity of this code: def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)"
- **Security Check**: "Check for security vulnerabilities in: import os; os.system(user_input)"
- **Git Operations**: "Get git status for server/git_server/git_server.py"
- **File Retrieval**: "Retrieve and analyze https://httpbin.org/json"

## Architecture

- **MultiServerMCPClient**: Main client class that manages connections
- **config_loader.py**: Configuration management utilities
- **client.py**: Main application with Gradio interface

## Dependencies

- `gradio`: Web interface
- `smolagents`: MCP client and agent framework
- `requests`: HTTP requests (for server health checks)

## Troubleshooting

1. **Server Connection Issues**: Ensure all servers are running on the correct ports
2. **API Key Issues**: Verify your Together AI API key is set correctly
3. **Tool Discovery**: Check server status to see which tools are available

## Development

The client is based on the `basic_client` structure but extended to support multiple servers. It automatically prefixes tool names to avoid conflicts and provides a unified interface for all operations.
