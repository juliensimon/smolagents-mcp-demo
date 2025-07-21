# Multi-Agent MCP Client

This client implements a multi-agent system using the smolagents library to coordinate specialized AI agents for different types of code analysis tasks.

## Architecture

The system consists of four main components:

### 1. Code Analysis Agent (coder-large)
- **Model**: `arcee-ai/coder-large`
- **Specialization**: Code metrics and security analysis
- **MCP Servers**:
  - Code Metrics Server
  - Code Security Server
- **Use Cases**: Code quality assessment, performance analysis, security audits

### 2. Research Agent (AFM-4.5B-Preview)
- **Model**: `arcee-ai/AFM-4.5B-Preview`
- **Specialization**: Code retrieval and git operations
- **MCP Servers**:
  - Code Retrieval Server
  - Git Repo Analysis Server
- **Use Cases**: Finding code examples, analyzing repositories

### 3. Web Search Agent (AFM-4.5B-Preview)
- **Model**: `arcee-ai/AFM-4.5B-Preview`
- **Specialization**: Web search and information gathering
- **Tools**: WebSearchTool()
- **Use Cases**: Finding current information, documentation, external resources

### 4. Manager Agent (maestro-reasoning)
- **Model**: `arcee-ai/maestro-reasoning`
- **Specialization**: Coordination and task delegation
- **Role**: Routes user requests to the appropriate specialized agent(s)

## Features

- **Specialized Agents**: Each agent is optimized for specific types of analysis
- **Intelligent Routing**: The manager agent automatically delegates tasks to the most appropriate agent
- **Unified Interface**: Single interface for all types of code analysis
- **Real-time Status**: Monitor agent and server status in real-time
- **Quick Actions**: Pre-configured analysis templates for common tasks

## Usage

### Running the Client

```bash
cd client/multi_agent_client
python client.py
```

### Prerequisites

1. **Environment Variables**:
   ```bash
   export TOGETHER_API_KEY="your_api_key_here"
   ```

2. **MCP Servers**: Ensure all required MCP servers are running:
   - Code Metrics Server (port 7862)
   - Code Security Server (port 7865)
   - Code Retrieval Server (port 7866)
   - Git Repo Analysis Server (port 7867)

### Interface

The client provides a Gradio web interface with:

- **Analysis Tab**: Main interface for code analysis requests
- **Agent Status Tab**: Real-time status of all agents and servers

### Example Requests

#### Security Analysis
```
Please perform a comprehensive security analysis on this code, identifying vulnerabilities and security best practices.
```

#### Code Metrics
```
Analyze this code for quality metrics, complexity, and maintainability characteristics.
```

#### Code Search
```
Find similar implementations or code examples for authentication patterns.
```

#### Git Analysis
```
Analyze this repository for commit patterns, branch strategy, and version control best practices.
```

#### Web Search
```
Search for current information about Python async programming best practices.
```

## Configuration

The client uses the centralized configuration from `config.json`:

```json
{
  "model": {
    "configs": {
      "arcee-ai/coder-large": { ... },
      "arcee-ai/afm": { ... },
      "arcee-ai/maestro-reasoning": { ... }
    }
  }
}
```

## Troubleshooting

### Common Issues

1. **Agent Not Initialized**: Check that all MCP servers are running and accessible
2. **Tool Not Found**: Verify server connections and tool availability
3. **Timeout Errors**: Try breaking down complex requests into simpler ones
4. **Authentication Errors**: Verify your API key is correctly set

### Debug Information

The client provides detailed logging during startup:
- Server connection status
- Tool availability per agent
- Agent initialization status

## Architecture Benefits

1. **Specialization**: Each agent is optimized for specific tasks
2. **Scalability**: Easy to add new agents for different specializations
3. **Reliability**: If one agent fails, others can continue working
4. **Efficiency**: Tasks are routed to the most appropriate agent automatically

## Future Enhancements

- Add more specialized agents (e.g., documentation, testing)
- Implement agent-to-agent communication
- Add support for custom agent configurations
- Implement result caching and optimization
