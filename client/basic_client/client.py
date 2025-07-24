"""MCP Basic Client providing a simple interface for sentiment analysis using MCP tools."""

import os
import sys

import gradio as gr
from smolagents import MCPClient, OpenAIServerModel, ToolCallingAgent

# Add the project root to the path to import the unified config_loader
sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ),
)


from config_loader import get_config_loader


def main():
    """Main function to run the basic client."""
    try:
        # Load unified configuration
        config_loader = get_config_loader()
        server_config = config_loader.get_server_config("basic_server")
        model_config = config_loader.get_model_config()

        # Get server URL
        server_url = server_config["url"]
        mcp_client = MCPClient({"url": server_url})
        tools = mcp_client.get_tools()

        # Get model configuration (can be changed via environment variable)
        model_name = os.getenv("TOGETHER_MODEL", model_config["default"])
        model_params = config_loader.get_model_params(model_name)
        api_base = model_config["api_base"]

        # Create model with OpenAIServerModel
        model = OpenAIServerModel(
            model_id=model_name,
            api_base=api_base,
            api_key=os.getenv("TOGETHER_API_KEY"),
            **model_params,
        )

        agent = ToolCallingAgent(
            tools=[*tools],
            model=model,
        )

        demo = gr.ChatInterface(
            fn=lambda message, history: str(agent.run(message)),
            type="messages",
            examples=[
                "Analyze the sentiment of the following text 'This is awesome'"
            ],
            title=f"MCP Basic Client - {model_name}",
            description=(
                f"Simple agent using MCP tools for text sentiment analysis. "
                f"**Model:** {model_name}"
            ),
        )

        demo.launch()
    finally:
        if "mcp_client" in locals():
            mcp_client.disconnect()


if __name__ == "__main__":
    main()
