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

import gradio as gr
from smolagents import (
    MCPClient,
    OpenAIServerModel,
    ToolCallingAgent,
    WebSearchTool,
)

from config_loader import get_config_loader

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


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
            model_params = get_model_params("arcee-ai/AFM-4.5B-Preview")
            agents["research"] = ToolCallingAgent(
                tools=research_tools,
                model=OpenAIServerModel(
                    model_id="arcee-ai/AFM-4.5B-Preview",
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
        model_params = get_model_params("arcee-ai/AFM-4.5B-Preview")
        agents["web_search"] = ToolCallingAgent(
            tools=[WebSearchTool()],
            model=OpenAIServerModel(
                model_id="arcee-ai/AFM-4.5B-Preview",
                api_base=api_base,
                api_key=api_key,
                **model_params,
            ),
            name="web_search_agent",
            description="Specialized in web search and information gathering.",
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
                model_id="arcee-ai/AFM-4.5B-Preview",  # Use AFM for manager (working)
                api_base=api_base,
                api_key=api_key,
                **get_model_params("arcee-ai/AFM-4.5B-Preview"),
            ),
            managed_agents=list(agents.values()),
            max_steps=3,  # Further limit steps
        )
        print(f"  ✅ Manager Agent: {len(agents)} managed agents")
    except Exception as e:
        print(f"  ❌ Failed to create Manager Agent: {e}")
        manager = None


def run_analysis(message: str) -> str:
    """Run analysis using the multi-agent system."""
    global manager
    if not manager:
        return "❌ Manager agent not initialized. Please check server connections and API configuration."

    if not agents:
        return "❌ No specialized agents available. Please check server connections."

    try:
        print(f"🎯 Running analysis: {message[:100]}...")

        # Validate input length to prevent model input errors
        if len(message) > 4000:  # Reduced limit to prevent 400 errors
            return "❌ **Input Too Long**: Your request is too long. Please break it down into smaller, more specific requests."

        # Clean the message to prevent malformed input
        cleaned_message = message.strip()
        if not cleaned_message:
            return "❌ **Empty Input**: Please provide a valid request."

        # Additional sanitization to prevent problematic characters
        cleaned_message = cleaned_message.replace("\x00", "").replace(
            "\r", "\n"
        )
        if len(cleaned_message) > 4000:
            cleaned_message = cleaned_message[:4000]

        result = manager.run(cleaned_message)
        return str(result)

    except Exception as e:
        error_msg = str(e)
        print(f"❌ Analysis error: {error_msg}")

        # Handle specific error types
        if "422" in error_msg and "unprocessable entity" in error_msg.lower():
            return f"""❌ **Model Input Error**

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
            return f"""❌ **Input Validation Error**

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
            return "⏱️ **Request Timeout**: The analysis took too long to complete. Please try with a smaller request or simpler question."
        elif (
            "authentication" in error_msg.lower() or "api" in error_msg.lower()
        ):
            return "🔑 **Authentication Error**: There may be an issue with the API configuration. Please check your settings and try again."
        else:
            return f"""❌ **Analysis Error**: {error_msg}

💡 **Troubleshooting:**
- Ensure your request is clear and specific
- Try breaking down complex requests
- Check that MCP servers are running
- Verify your API configuration"""


def get_status() -> str:
    """Get simple status of all agents."""
    servers = load_servers()
    status = [
        "# Multi-Agent System Status",
        "",
        f"**Total Agents:** {len(agents) + (1 if manager else 0)}",
        f"**Connected Servers:** {len(mcp_clients)}/{len(servers)}",
        "",
        "## Agents:",
    ]

    for name, agent in agents.items():
        tool_count = len(agent.tools) if hasattr(agent, "tools") else 0
        status.append(f"- **{name}**: {tool_count} tools")

    if manager:
        status.append("- **Manager**: Active")

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
    if not message.strip():
        return "", chat_history

    # Add user message with correct format
    chat_history.append({"role": "user", "content": message})

    try:
        response = run_analysis(message)
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
        if "422" in error_msg and "unprocessable entity" in error_msg.lower():
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
        else:
            response = f"❌ Error: {error_msg}"

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

        with gr.Blocks(title="Simple Multi-Agent Code Analysis") as demo:
            gr.Markdown(
                """
                # Simple Multi-Agent Code Analysis Platform

                **Agents:**
                - Code Analysis Agent (arcee-ai/coder-large): Code metrics and security
                - Research Agent (arcee-ai/AFM-4.5B-Preview): Code retrieval and git operations
                - Web Search Agent (arcee-ai/AFM-4.5B-Preview): Web search and information gathering
                - Manager Agent (arcee-ai/AFM-4.5B-Preview): Coordinates all agents
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
                        height=400, label="Analysis Results", type="messages"
                    )

                    with gr.Row():
                        submit_btn = gr.Button("Analyze", variant="primary")
                        clear = gr.Button("Clear", variant="secondary")

                    # Event handlers
                    msg.submit(
                        respond, inputs=[msg, chatbot], outputs=[msg, chatbot]
                    )
                    submit_btn.click(
                        respond, inputs=[msg, chatbot], outputs=[msg, chatbot]
                    )
                    clear.click(clear_chat, outputs=[chatbot])

                with gr.Tab("Status"):
                    status_display = gr.Markdown(get_status())
                    refresh_btn = gr.Button("Refresh Status")
                    refresh_btn.click(refresh_status, outputs=status_display)

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
