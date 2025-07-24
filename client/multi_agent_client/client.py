#!/usr/bin/env python3
"""
Simplified Multi-Agent MCP Client

A streamlined client that uses specialized agents with different MCP servers:
- Code Analysis Agent: Code metrics and security analysis
- Research Agent: Code retrieval and git operations
- Web Search Agent: Web search and information gathering
- Manager Agent: Coordinates all agents
"""

import os
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import gradio as gr
from smolagents import (
    MCPClient,
    OpenAIServerModel,
    ToolCallingAgent,
    WebSearchTool,
)

from config_loader import get_config_loader


def load_config():
    """Load the main configuration."""
    return get_config_loader().get_config()


def load_servers():
    """Load server configurations."""
    return get_config_loader().get_servers()


def load_api_base():
    """Load the API base URL from model configuration."""
    return get_config_loader().get_model_api_base()


def get_model_params(model_name):
    """Get model parameters from configuration."""
    return get_config_loader().get_model_params(model_name)


# Global variables to store our agents and clients
mcp_clients = {}
agents = {}
manager = None


def setup_connections():
    """Setup connections to MCP servers."""
    global mcp_clients
    servers = load_servers()

    print("🔌 Connecting to MCP servers...")

    for server_key, server_config in servers.items():
        try:
            print(f"  Connecting to {server_config['name']}...")
            mcp_client = MCPClient(
                {
                    "url": server_config["url"],
                    "transport": "sse",
                }
            )
            tools = mcp_client.get_tools()
            mcp_clients[server_key] = mcp_client
            print(f"  ✅ {server_config['name']}: {len(tools)} tools")

        except Exception as e:
            print(f"  ❌ Failed to connect to {server_config['name']}: {e}")


def setup_agents():
    """Setup specialized agents."""
    global agents
    api_base = load_api_base()
    api_key = os.getenv("TOGETHER_API_KEY")

    if not api_key:
        print("  ❌ TOGETHER_API_KEY environment variable not set")
        return

    # Code Analysis Agent
    code_tools = []
    if "code_metrics" in mcp_clients:
        code_tools.extend(mcp_clients["code_metrics"].get_tools())
    if "code_security" in mcp_clients:
        code_tools.extend(mcp_clients["code_security"].get_tools())

    if code_tools:
        try:
            model_params = get_model_params("arcee-ai/coder-large")
            agents["code_analysis"] = ToolCallingAgent(
                tools=code_tools,
                model=OpenAIServerModel(
                    model_id="arcee-ai/coder-large",
                    api_base=api_base,
                    api_key=api_key,
                    **model_params,
                ),
                name="code_analysis_agent",
                description="Specialized in code analysis, metrics, and security.",
            )
            print(f"  ✅ Code Analysis Agent: {len(code_tools)} tools")
        except Exception as e:
            print(f"  ❌ Failed to create Code Analysis Agent: {e}")

    # Research Agent
    research_tools = []
    if "code_retrieval" in mcp_clients:
        research_tools.extend(mcp_clients["code_retrieval"].get_tools())
    if "git_repo_analysis" in mcp_clients:
        research_tools.extend(mcp_clients["git_repo_analysis"].get_tools())

    if research_tools:
        try:
            model_params = get_model_params("arcee-ai/coder-large")
            agents["research"] = ToolCallingAgent(
                tools=research_tools,
                model=OpenAIServerModel(
                    model_id="arcee-ai/coder-large",
                    api_base=api_base,
                    api_key=api_key,
                    **model_params,
                ),
                name="research_agent",
                description="Specialized in code retrieval and git operations.",
            )
            print(f"  ✅ Research Agent: {len(research_tools)} tools")
        except Exception as e:
            print(f"  ❌ Failed to create Research Agent: {e}")

    # Web Search Agent
    try:
        model_params = get_model_params("arcee-ai/coder-large")
        agents["web_search"] = ToolCallingAgent(
            tools=[WebSearchTool()],
            model=OpenAIServerModel(
                model_id="arcee-ai/coder-large",
                api_base=api_base,
                api_key=api_key,
                **model_params,
            ),
            name="web_search_agent",
            description="Specialized in finding additional information about problems, errors, and technical concepts. Use for researching error messages, understanding technical issues, finding best practices, and gathering context about problems. Do NOT use for fetching files or downloading code - focus on informational research only.",
        )
        print("  ✅ Web Search Agent ready")
    except Exception as e:
        print(f"  ❌ Failed to create Web Search Agent: {e}")


def setup_manager():
    """Setup the manager agent."""
    global manager
    if not agents:
        print("  ⚠️ No agents available for manager")
        return

    api_base = load_api_base()
    api_key = os.getenv("TOGETHER_API_KEY")

    if not api_key:
        print("  ❌ TOGETHER_API_KEY environment variable not set")
        return

    try:
        manager = ToolCallingAgent(
            tools=[],
            model=OpenAIServerModel(
                model_id="arcee-ai/coder-large",
                api_base=api_base,
                api_key=api_key,
                **get_model_params("arcee-ai/coder-large"),
            ),
            managed_agents=list(agents.values()),
            max_steps=5,
        )
        print(f"  ✅ Manager Agent: {len(agents)} managed agents")
    except Exception as e:
        print(f"  ❌ Failed to create Manager Agent: {e}")
        manager = None


def get_status() -> str:
    """Get simple status of all agents."""
    servers = load_servers()
    config_loader = get_config_loader()
    default_model = config_loader.get_model_config()["default"]
    model_name = os.getenv("TOGETHER_MODEL", default_model)

    status = [
        "# Multi-Agent System Status",
        "",
        f"**Model:** `{model_name}`",
        f"**Total Agents:** {len(agents) + (1 if manager else 0)}",
        f"**Connected Servers:** {len(mcp_clients)}/{len(servers)}",
        "",
        "## Agents:",
    ]

    for name, agent in agents.items():
        tool_count = len(agent.tools) if hasattr(agent, "tools") else 0
        status.append(f"- **{name}** (`{model_name}`): {tool_count} tools")

    if manager:
        status.append(f"- **Manager** (`{model_name}`): Active")

    status.append("")
    status.append("## Servers:")
    for server_key, server_config in servers.items():
        status_text = (
            "Connected" if server_key in mcp_clients else "Disconnected"
        )
        status.append(f"- **{server_config['name']}**: {status_text}")

    return "\n".join(status)


def disconnect():
    """Disconnect from all MCP servers."""
    servers = load_servers()
    for server_key, client in mcp_clients.items():
        try:
            client.disconnect()
            print(f"Disconnected from {servers[server_key]['name']}")
        except Exception as e:
            print(
                f"Error disconnecting from {servers[server_key]['name']}: {e}"
            )


def respond(message, chat_history):
    """Handle chat responses."""
    global manager

    if not message.strip():
        return "", chat_history

    # Add user message with correct format
    chat_history.append({"role": "user", "content": message})

    try:
        # Check if manager is available
        if not manager:
            response = "❌ Manager agent not initialized. Please check server connections and API configuration."
        elif not agents:
            response = "❌ No specialized agents available. Please check server connections."
        else:
            print(f"🎯 Running analysis: {message[:100]}...")
            # Actually call the manager to get a response
            try:
                result = manager.run(message)
                response = (
                    result.content
                    if hasattr(result, "content")
                    else str(result)
                )
            except Exception as e:
                response = f"❌ Error during analysis: {str(e)}"

        if not response or response.strip() == "":
            response = (
                "⚠️ No results returned. Please try rephrasing your request."
            )

        # Add assistant response with correct format
        chat_history.append({"role": "assistant", "content": response})
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Response error: {error_msg}")

        # Handle specific error types
        if "500" in error_msg and "internal server error" in error_msg.lower():
            response = f"""❌ **Server Error (500)**

The Together AI server encountered an internal error. This can happen when:
- The server is temporarily overloaded
- There's an issue with the model or API endpoint
- The request is too complex for the current server state

**Error Details:** {error_msg}

💡 **Try:**
- Wait a moment and try again
- Break down your request into smaller parts
- Try a simpler, more direct question
- Check if the Together AI service is experiencing issues"""
        elif (
            "422" in error_msg and "unprocessable entity" in error_msg.lower()
        ):
            response = f"""❌ **Model Input Error**

The model received invalid input that it couldn't process. This can happen when:
- The input is too long or complex
- The model receives malformed data from tools
- There's an issue with the model configuration

**Error Details:** {error_msg}

💡 **Try:**
- Breaking down your request into smaller, simpler parts
- Using more specific and clear language
- Checking that all MCP servers are properly connected"""
        elif (
            "input validation error" in error_msg.lower() or "400" in error_msg
        ):
            response = f"""❌ **Input Validation Error**

The model encountered an input validation error. This can happen when:
- The input is too long or complex
- The model receives malformed data from tools
- The response from a tool is too large

**Error Details:** {error_msg}

💡 **Try:**
- Breaking down your request into smaller, simpler parts
- Using more specific and focused questions
- Avoiding requests that might generate very large responses"""
        elif "timeout" in error_msg.lower():
            response = "⏱️ **Request Timeout**: The analysis took too long to complete. Please try with a smaller request or simpler question."
        elif (
            "authentication" in error_msg.lower() or "api" in error_msg.lower()
        ):
            response = "🔑 **Authentication Error**: There may be an issue with the API configuration. Please check your settings and try again."
        else:
            response = f"""❌ **Analysis Error**: {error_msg}

💡 **Troubleshooting:**
- Ensure your request is clear and specific
- Try breaking down complex requests
- Check that MCP servers are running
- Verify your API configuration"""

        chat_history.append({"role": "assistant", "content": response})

    return "", chat_history


def clear_chat():
    """Clear the chat history."""
    return []


def refresh_status():
    """Refresh the status display."""
    return get_status()


def create_interface():
    """Create a simplified Gradio interface."""
    try:
        # Initialize the system
        setup_connections()
        setup_agents()
        setup_manager()

        # Get model information for display
        config_loader = get_config_loader()
        default_model = config_loader.get_model_config()["default"]
        model_name = os.getenv("TOGETHER_MODEL", default_model)

        with gr.Blocks(
            title=f"Multi-Agent MCP Analysis - {model_name}"
        ) as demo:
            gr.Markdown(
                f"""
                # Multi-Agent MCP Analysis Platform

                **Model:** `{model_name}`

                **Specialized MCP Servers:**
                - 🔍 **Code Retrieval Server**: Find and retrieve code files
                - 📊 **Code Metrics Server**: Analyze complexity, maintainability, and code quality
                - 🔒 **Code Security Server**: Detect vulnerabilities and security issues
                - 📝 **Basic Server**: Sentiment analysis of text content
                - 🗂️ **Git Repo Analysis Server**: Analyze git history and repository structure

                **AI Agents:**
                - Code Analysis Agent (`{model_name}`): Code metrics and security analysis
                - Research Agent (`{model_name}`): Code retrieval and git operations
                - Manager Agent (`{model_name}`): Coordinates all agents
                """
            )

            with gr.Tabs():
                with gr.Tab("Analysis"):
                    msg = gr.Textbox(
                        label="Analysis Request",
                        placeholder="Describe what you'd like to analyze...",
                        lines=3,
                    )

                    chatbot = gr.Chatbot(
                        label="Analysis Results", type="messages"
                    )

                    with gr.Row():
                        submit_btn = gr.Button("Analyze", variant="primary")
                        clear = gr.Button("Clear", variant="secondary")

                    # Event handlers
                    msg.submit(  # type: ignore[attr-defined]
                        respond, inputs=[msg, chatbot], outputs=[msg, chatbot]
                    )
                    submit_btn.click(  # type: ignore[attr-defined]
                        respond, inputs=[msg, chatbot], outputs=[msg, chatbot]
                    )
                    clear.click(clear_chat, outputs=[chatbot])  # type: ignore[attr-defined]

                with gr.Tab("Status"):
                    status_display = gr.Markdown(get_status())
                    refresh_btn = gr.Button("Refresh Status")
                    refresh_btn.click(refresh_status, outputs=[status_display])  # type: ignore[attr-defined]

        return demo

    except Exception as e:
        print(f"Error initializing client: {e}")
        return None


def main():
    """Main function to run the simplified client."""
    demo = create_interface()

    if demo:
        try:
            config = load_config()
            gradio_config = config.get("client", {}).get("gradio", {})

            demo.launch(
                server_name=gradio_config.get("server_name", "127.0.0.1"),
                server_port=gradio_config.get("server_port", 7864),
                share=gradio_config.get("share", False),
                show_error=gradio_config.get("show_error", True),
            )
        except Exception as e:
            print(f"Failed to launch interface: {e}")
            try:
                demo.launch(share=False, show_error=True)
            except Exception as e2:
                print(f"Failed to launch on any port: {e2}")
        finally:
            disconnect()
    else:
        print("Failed to create interface. Check your configuration.")


if __name__ == "__main__":
    main()
