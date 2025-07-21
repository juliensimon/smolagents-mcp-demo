# Basic Client

This folder contains the basic MCP client implementation with Gradio interface.

## Files

- `client.py` - Basic client with Gradio chat interface and AI agent integration
- `config_loader.py` - Configuration loading utilities
- `config.json` - Configuration file for server URL and model settings
- `__init__.py` - Package initialization file

## Features

- Gradio web interface for interactive chat
- Integration with AI models via Together AI
- CodeAgent for intelligent tool usage
- Environment variable configuration support
- Full-featured MCP client with AI integration

## Usage

```bash
python client.py
```

This will start a Gradio web interface where you can interact with the MCP tools through an AI agent.

## Environment Variables

- `TOGETHER_API_KEY` - Your Together AI API key
- `TOGETHER_MODEL` - Model to use (default: arcee-ai/AFM-4.5B-Preview)

## Configuration

Edit `config.json` to change:
- Server URL
- Model settings
- API configuration
- System prompts
