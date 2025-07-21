# MCP Demo Project

A comprehensive demonstration of Model Context Protocol (MCP) servers and clients, showcasing various AI-powered tools and integrations.

## 🏗️ Project Structure

```
mcp-demo/
├── config.json              # Unified configuration for all components
├── config_loader.py         # Unified configuration loader
├── start_all_servers.py     # Script to start all MCP servers
├── server/                  # MCP server implementations
│   ├── basic_server/        # Basic text sentiment analysis
│   ├── code_metrics_server/ # Code analysis and metrics
│   ├── code_security_server/# Security vulnerability detection
│   ├── code_retriever_server/# HTTP file retrieval and analysis
│   └── git_server/          # Git repository operations
├── client/                  # MCP client implementations
│   ├── basic_client/        # Simple client for basic server
│   ├── code_client/         # Multi-server client with advanced features
│   └── multi_agent_client/  # Multi-agent system with specialized agents
└── tests/                   # Test suite
    ├── run_tests.py         # Test runner
    └── test_config.py       # Configuration tests
```

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** installed
2. **Git** for repository operations
3. **Together AI API Key** (set as environment variable):
   ```bash
   export TOGETHER_API_KEY="your-api-key-here"
   ```

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd mcp-demo
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start all MCP servers**:
   ```bash
   python start_all_servers.py
   ```

4. **Run a client** (in a new terminal):
   ```bash
   # Basic client
   python client/basic_client/client.py

   # Multi-server client
   python client/code_client/client.py

   # Multi-agent client (recommended)
   python client/multi_agent_client/client.py
   ```

## 🔧 Configuration

The project uses a **unified configuration system** with a single `config.json` file that defines:

- **Server configurations**: Ports, URLs, and paths for all MCP servers
- **Model settings**: Together AI model parameters and API configuration
- **Client settings**: Gradio interface configuration
- **Testing parameters**: Timeouts, retry attempts, and health check intervals
- **Logging settings**: Log levels, file paths, and formats

### Server Ports

| Server | Port | Description |
|--------|------|-------------|
| Basic Server | 7860 | Text sentiment analysis |
| Code Metrics | 7862 | Code analysis and metrics |
| Code Security | 7865 | Security vulnerability detection |
| Code Retrieval | 7866 | HTTP file retrieval and analysis |
| Git Repo Analysis | 7867 | Git repository operations |

### Configuration Management

- **Single Source of Truth**: All configuration is centralized in `config.json`
- **Automatic Validation**: Configuration is validated for correctness
- **Easy Maintenance**: Changes only need to be made in one place
- **Component Independence**: All components use the same configuration

For detailed configuration documentation, see [CONFIGURATION.md](CONFIGURATION.md).

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python tests/run_tests.py all

# Run quick tests (environment and configuration only)
python tests/run_tests.py quick

# Run specific test categories
python tests/run_tests.py integration
python tests/run_tests.py configuration
python tests/run_tests.py environment

# List available test categories
python tests/run_tests.py list
```

## 📊 Available Servers

### 1. Basic Server (Port 7860)
- **Functionality**: Text sentiment analysis
- **Tools**: Sentiment analysis with polarity and subjectivity scoring
- **Use Case**: Analyzing emotional tone in text

### 2. Code Metrics Server (Port 7862)
- **Functionality**: Code analysis and quality metrics
- **Tools**: Complexity analysis, style checking, maintainability index
- **Use Case**: Code quality assessment and optimization

### 3. Code Security Server (Port 7865)
- **Functionality**: Security vulnerability detection
- **Tools**: SQL injection, command injection, hardcoded secrets detection
- **Use Case**: Security auditing and vulnerability assessment

### 4. Code Retrieval Server (Port 7866)
- **Functionality**: HTTP file retrieval and analysis
- **Tools**: URL validation, file content retrieval, content analysis
- **Use Case**: Remote file processing and analysis

### 5. Git Repo Analysis Server (Port 7867)
- **Functionality**: Git repository operations
- **Tools**: Git status, commit, diff, log analysis
- **Use Case**: Version control and repository management

## 🎯 Available Clients

### Basic Client
- **Purpose**: Simple interface for basic server functionality
- **Features**: Chat interface with sentiment analysis
- **Usage**: `python client/basic_client/client.py`

### Multi-Server Client
- **Purpose**: Advanced interface for all MCP servers
- **Features**:
  - Multi-server tool integration
  - Server selection and management
  - Advanced chat interface
  - Example workflows
- **Usage**: `python client/code_client/client.py`

### Multi-Agent Client (Recommended)
- **Purpose**: Intelligent multi-agent system with specialized agents
- **Features**:
  - **Code Analysis Agent** (coder-large): Code metrics and security analysis
  - **Research Agent** (AFM-4.5B-Preview): Code retrieval, git operations, and web search
  - **Manager Agent** (maestro-reasoning): Intelligent task delegation
  - Automatic agent selection based on task type
  - Unified interface for all analysis types
  - Real-time agent status monitoring
- **Usage**: `python client/multi_agent_client/client.py`
- **Test**: `python client/multi_agent_client/test_multi_agent.py`

## 🔄 Workflow Examples

### Code Analysis Workflow
1. **Retrieve code** from a URL using Code Retrieval Server
2. **Analyze complexity** using Code Metrics Server
3. **Check security** using Code Security Server
4. **Commit changes** using Git Repo Analysis Server

### Text Analysis Workflow
1. **Analyze sentiment** using Basic Server
2. **Process results** through the multi-server client
3. **Generate insights** using AI model integration

## 🛠️ Development

### Adding New Servers

1. **Add server configuration** to `config.json`:
   ```json
   "new_server": {
     "name": "New Server",
     "port": 7868,
     "url": "http://127.0.0.1:7868/gradio_api/mcp/sse",
     "description": "New server functionality",
     "path": "server/new_server/new_server.py"
   }
   ```

2. **Create server implementation** in `server/new_server/`
3. **Update server to use unified configuration**
4. **Add tests** to the test suite

### Code Quality

The project uses pre-commit hooks for code quality:

```bash
# Install pre-commit hooks
./setup_precommit.sh

# Run pre-commit on all files
pre-commit run --all-files
```

## 📝 API Documentation

Each server provides detailed API documentation through their Gradio interfaces. Access them at:
- Basic Server: http://127.0.0.1:7860
- Code Metrics: http://127.0.0.1:7862
- Code Security: http://127.0.0.1:7865
- Code Retrieval: http://127.0.0.1:7866
- Git Repo Analysis: http://127.0.0.1:7867

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Run tests** to ensure everything works
5. **Submit a pull request**

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports are not already in use
2. **API key issues**: Verify `TOGETHER_API_KEY` is set correctly
3. **Import errors**: Check that all dependencies are installed
4. **Configuration errors**: Run `python config_loader.py` to validate configuration

### Getting Help

- Check the [CONFIGURATION.md](CONFIGURATION.md) for detailed configuration information
- Review server-specific README files in the `server/` directory
- Check the test suite for usage examples
- Open an issue for bugs or feature requests
