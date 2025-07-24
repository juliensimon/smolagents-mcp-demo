#!/usr/bin/env python3
"""
Multi-Server MCP Client

This client connects to multiple MCP servers and provides a unified interface:
- Code Retriever Server: HTTP file retrieval and analysis
- Code Metrics Server: Code analysis and metrics
- Code Security Server: Security vulnerability detection
- Git Server: Git operations

Based on the test client structure but extended for multiple servers.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict

# Add the project root to the path so we can import the shared config_loader
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import gradio as gr
from smolagents import MCPClient, OpenAIServerModel, ToolCallingAgent

from config_loader import get_config_loader


# Create wrapper functions to match the expected interface
def load_config():
    """Load the main configuration."""
    return get_config_loader().get_config()


def load_servers():
    """Load server configurations."""
    return get_config_loader().get_servers()


def load_api_base():
    """Load the API base URL from model configuration."""
    return get_config_loader().get_model_api_base()


class MultiServerMCPClient:
    """Client that connects to multiple MCP servers."""

    def __init__(self):
        self.servers = load_servers()
        self.mcp_clients = {}
        self.all_tools = []
        self.agent = None
        self.enabled_servers = set()  # Track which servers are enabled
        self.setup_connections()
        self.setup_agent()

    def setup_connections(self):
        """Setup connections to all MCP servers."""
        print("🔌 Connecting to MCP servers...")

        for server_key, server_config in self.servers.items():
            try:
                print(
                    f"  Connecting to {server_config['name']} at {server_config['url']}"
                )
                mcp_client = MCPClient(
                    {
                        "url": server_config["url"],
                        "transport": "sse",  # Explicitly specify transport
                    }
                )
                tools = mcp_client.get_tools()

                # Add server context to tool descriptions for clarity
                for tool in tools:
                    tool.description = (
                        f"[{server_config['name']}] {tool.description}"
                    )

                self.mcp_clients[server_key] = mcp_client
                self.all_tools.extend(tools)
                print(
                    f"  ✅ {server_config['name']}: {len(tools)} tools available"
                )

            except Exception as e:
                print(
                    f"  ❌ Failed to connect to {server_config['name']}: {e}"
                )

        print(f"📊 Total tools available: {len(self.all_tools)}")

        # Validate tool availability
        self._validate_tools()

        # Enable all connected servers by default
        self.enabled_servers = set(self.mcp_clients.keys())

    def _validate_tools(self):
        """Validate that all tools are properly accessible."""
        if not self.all_tools:
            print("⚠️ Warning: No tools loaded!")
            return

        print("🔍 Validating tool accessibility...")
        valid_tools = []

        for tool in self.all_tools:
            try:
                # Basic validation - check if tool has required attributes
                if hasattr(tool, "name") and hasattr(tool, "description"):
                    valid_tools.append(tool)
                else:
                    print(
                        f"  ❌ Invalid tool format: {getattr(tool, 'name', 'unknown')}"
                    )
            except Exception as e:
                print(f"  ❌ Tool validation failed: {e}")

        self.all_tools = valid_tools
        print(f"✅ {len(valid_tools)} valid tools confirmed")

    def setup_agent(self):
        """Setup the ToolCallingAgent with all available tools."""
        if not self.all_tools:
            print(
                "⚠️ No tools available! Agent will run without tool capabilities."
            )
            return

        # Get model configuration
        config_loader = get_config_loader()
        model_name = os.getenv(
            "TOGETHER_MODEL", config_loader.get_model_config()["default"]
        )
        api_base = load_api_base()

        # Create model with OpenAIServerModel
        model = OpenAIServerModel(
            model_id=model_name,
            api_base=api_base,
            api_key=os.getenv("TOGETHER_API_KEY"),
        )

        # Create agent with validated tools only
        try:
            self.agent = ToolCallingAgent(
                tools=self.all_tools,
                model=model,
            )

            # Print available tools for debugging
            print(f"🔧 Agent initialized with {len(self.all_tools)} tools:")

        except Exception as e:
            print(f"❌ Failed to initialize agent: {e}")
            self.agent = None

    def _get_available_tools_summary(self) -> str:
        """Get a summary of available tools for the model."""
        if not self.all_tools:
            return "No tools available"

        summary_lines = []
        for tool in self.all_tools:
            summary_lines.append(f"- {tool.name}: {tool.description}")

        return "\n".join(summary_lines)

    def get_server_status(self) -> str:
        """Get status of all MCP servers."""
        status_lines = ["# 📊 Server Status", ""]

        for server_key, server_config in self.servers.items():
            if server_key in self.mcp_clients:
                try:
                    # Test connection by getting tools
                    tools = self.mcp_clients[server_key].get_tools()
                    status_lines.append(
                        f"✅ **{server_config['name']}**: Connected ({len(tools)} tools)"
                    )
                    status_lines.append(f"   - URL: {server_config['url']}")
                    status_lines.append(
                        f"   - Description: {server_config['description']}"
                    )
                    status_lines.append("")
                except Exception as e:
                    status_lines.append(
                        f"❌ **{server_config['name']}**: Connection Error - {str(e)}"
                    )
                    status_lines.append("")
            else:
                status_lines.append(
                    f"❌ **{server_config['name']}**: Not Connected"
                )
                status_lines.append("")

        status_lines.append(
            f"📋 **Total Tools Available**: {len(self.all_tools)}"
        )

        if self.all_tools:
            status_lines.append("")
            status_lines.append("## 🔧 Available Tools")
            for i, tool in enumerate(self.all_tools[:10], 1):
                status_lines.append(
                    f"{i}. **{tool.name}**: {tool.description[:100]}..."
                )
            if len(self.all_tools) > 10:
                status_lines.append(
                    f"... and {len(self.all_tools) - 10} more tools"
                )

        return "\n".join(status_lines)

    def test_tool_connectivity(self) -> dict:
        """Test connectivity and functionality of all tools."""
        results: Dict[str, Any] = {
            "total_tools": len(self.all_tools),
            "server_status": {},
            "tool_status": "operational" if self.all_tools else "no_tools",
        }

        for server_key, server_config in self.servers.items():
            if server_key in self.mcp_clients:
                try:
                    # Test if we can still get tools from this server
                    tools = self.mcp_clients[server_key].get_tools()
                    results["server_status"][server_key] = {
                        "status": "connected",
                        "tools_count": len(tools),
                        "name": server_config["name"],
                    }
                except Exception as e:
                    results["server_status"][server_key] = {
                        "status": "error",
                        "error": str(e),
                        "name": server_config["name"],
                    }
            else:
                results["server_status"][server_key] = {
                    "status": "not_connected",
                    "name": server_config["name"],
                }

        return results

    def disconnect(self):
        """Disconnect from all MCP servers."""
        for server_key, client in self.mcp_clients.items():
            try:
                client.disconnect()
                print(f"Disconnected from {self.servers[server_key]['name']}")
            except Exception as e:
                print(
                    f"Error disconnecting from {self.servers[server_key]['name']}: {e}"
                )

    def get_server_tools(self, server_key):
        """Get tools for a specific server."""
        if server_key in self.mcp_clients:
            try:
                return self.mcp_clients[server_key].get_tools()
            except Exception as e:
                print(f"Error getting tools for {server_key}: {e}")
                return []
        return []

    def set_enabled_servers(self, enabled_servers):
        """Set which servers are enabled and update the agent."""
        self.enabled_servers = set(enabled_servers)
        self._update_agent_tools()

    def _update_agent_tools(self):
        """Update the agent with only tools from enabled servers."""
        if not self.enabled_servers:
            self.all_tools = []
            print("🔧 No servers enabled - agent has no tools")
            return

        # Collect tools only from enabled servers
        enabled_tools = []
        for server_key in self.enabled_servers:
            if server_key in self.mcp_clients:
                try:
                    tools = self.mcp_clients[server_key].get_tools()
                    # Tools already have server context from initial setup
                    enabled_tools.extend(tools)
                    print(
                        f"🔧 Added {len(tools)} tools from {self.servers[server_key]['name']}"
                    )
                except Exception as e:
                    print(f"Error getting tools from {server_key}: {e}")

        self.all_tools = enabled_tools

        # Reinitialize agent with new tools
        if self.all_tools:
            print(
                f"🔧 Reinitializing agent with {len(self.all_tools)} total tools"
            )
            self.setup_agent()
        else:
            print("🔧 No tools available - agent disabled")
            self.agent = None


def create_multi_server_interface():
    """Create a Gradio interface for testing multi-server MCP functionality."""

    try:
        # Initialize the multi-server client
        client = MultiServerMCPClient()

        # Get model name for display
        model_name = os.getenv("TOGETHER_MODEL", "arcee-ai/coder-large")

        # Create minimal Gradio interface with default theme
        with gr.Blocks(title="Code Analysis Platform") as demo:
            # Header section
            with gr.Row():
                with gr.Column():
                    gr.Markdown(
                        f"""
                    # Code Analysis Platform

                    Analyze code for security, performance, and quality issues using AI-powered tools.

                    **Model:** `{model_name}` | **Status:** Ready | **Tools:** {len(client.all_tools)} available
                    """
                    )

            with gr.Tabs():
                with gr.Tab("Analysis", elem_classes="tab-nav"):
                    # Code input at the top
                    msg = gr.Textbox(
                        label="Code Input",
                        placeholder="Paste your code or describe what you'd like to analyze...",
                        lines=3,
                    )

                    # Analysis results in the middle
                    chatbot = gr.Chatbot(
                        height=400, label="Analysis Results", type="messages"
                    )

                    # Analyze and Clear buttons side by side at the bottom
                    with gr.Row():
                        submit_btn = gr.Button("Analyze", variant="primary")
                        clear = gr.Button("Clear Chat", variant="secondary")

                    # Quick analysis templates
                    gr.Markdown("### Quick Analysis")
                    with gr.Row():
                        quick_security = gr.Button("Security", size="sm")
                        quick_performance = gr.Button("Performance", size="sm")
                        quick_quality = gr.Button("Quality", size="sm")
                        quick_git = gr.Button("Git", size="sm")

                    status = gr.Textbox(
                        label="Status", interactive=False, visible=False
                    )

                    def respond(message, chat_history):
                        if not message.strip():
                            return "", chat_history, "Please enter a message."

                        try:
                            # Add user message to history with loading state
                            chat_history.append(
                                {"role": "user", "content": message}
                            )
                            chat_history.append(
                                {
                                    "role": "assistant",
                                    "content": "🔄 Analyzing your code...",
                                }
                            )

                            # Check if agent is available
                            if not client.agent:
                                response = "❌ Agent not initialized. Please check server connections and try again."
                            elif not client.all_tools:
                                response = "⚠️ No tools available. The agent can provide general responses but cannot perform code analysis."
                            else:
                                # Create minimal enhanced message with tool context
                                enhanced_message = f"""Use available tools: {client._get_available_tools_summary()}

User request: {message}"""

                            # Get response from agent
                            result = client.agent.run(enhanced_message)
                            response = str(result)

                            # Handle empty responses
                            if not response or response.strip() == "":
                                response = "⚠️ The analysis completed but returned no results. Please try rephrasing your request or check if the code/question is valid."

                            # Update the last message with the response
                            chat_history[-1] = {
                                "role": "assistant",
                                "content": response,
                            }

                            return "", chat_history, ""
                        except Exception as e:
                            error_msg = str(e)

                            # Handle specific error types
                            if (
                                "tool" in error_msg.lower()
                                and "not found" in error_msg.lower()
                            ):
                                response = f"""❌ **Tool Not Found Error**

The model tried to use a tool that doesn't exist. This can happen when:
- The model hallucinates a tool name
- There's a connectivity issue with the servers

**Available Tools:** {', '.join([tool.name for tool in client.all_tools[:5]])}{'...' if len(client.all_tools) > 5 else ''}

Please try your request again, or check the Server Status tab to ensure all servers are connected."""
                            elif "timeout" in error_msg.lower():
                                response = "⏱️ **Request Timeout**: The analysis took too long to complete. Please try with a smaller code snippet or simpler request."
                            elif (
                                "authentication" in error_msg.lower()
                                or "api" in error_msg.lower()
                            ):
                                response = "🔑 **Authentication Error**: There may be an issue with the API configuration. Please check your settings and try again."
                            else:
                                response = f"""❌ **Analysis Error**: {error_msg}

💡 **Troubleshooting Tips:**
- Ensure your code is properly formatted
- Try breaking down complex requests into simpler ones
- Check that all MCP servers are running (Server Status tab)
- Verify your API configuration"""

                            # Update the last message with error
                            if chat_history and "🔄" in str(
                                chat_history[-1].get("content", "")
                            ):
                                chat_history[-1] = {
                                    "role": "assistant",
                                    "content": response,
                                }
                            else:
                                chat_history.append(
                                    {"role": "assistant", "content": response}
                                )
                            return (
                                "",
                                chat_history,
                                f"Error occurred: {str(e)}",
                            )

                    def clear_chat():
                        return []

                    def quick_action(action_type, current_msg):
                        prompts = {
                            "security": "Please perform a comprehensive security analysis on the following code, identifying vulnerabilities, potential attack vectors, and security best practices:",
                            "performance": "Please analyze the following code for performance issues, bottlenecks, optimization opportunities, and efficiency improvements:",
                            "quality": "Please evaluate the following code for quality issues, maintainability, readability, and adherence to best practices:",
                            "git": "Please analyze this repository or code for git-related issues, commit patterns, branch strategy, and version control best practices:",
                        }
                        return (
                            prompts.get(action_type, "") + "\n\n" + current_msg
                        )

                    # Event handlers
                    msg.submit(respond, [msg, chatbot], [msg, chatbot, status])
                    submit_btn.click(
                        respond, [msg, chatbot], [msg, chatbot, status]
                    )
                    clear.click(clear_chat, outputs=[chatbot])

                    # Quick action handlers
                    quick_security.click(
                        lambda msg: quick_action("security", msg),
                        inputs=[msg],
                        outputs=[msg],
                    )
                    quick_performance.click(
                        lambda msg: quick_action("performance", msg),
                        inputs=[msg],
                        outputs=[msg],
                    )
                    quick_quality.click(
                        lambda msg: quick_action("quality", msg),
                        inputs=[msg],
                        outputs=[msg],
                    )
                    quick_git.click(
                        lambda msg: quick_action("git", msg),
                        inputs=[msg],
                        outputs=[msg],
                    )

                    # Code Analysis Examples
                    gr.Markdown("### Code Analysis Examples")

                    # Example 1: Web Security Vulnerabilities
                    gr.Markdown("**1. Web Security Vulnerabilities**")
                    gr.Code(
                        """
import sqlite3
import os
from flask import Flask, request

app = Flask(__name__)
app.secret_key = "hardcoded_secret_key_123"

class UserService:
    def __init__(self):
        self.db_path = "users.db"

    def authenticate_user(self, username, password):
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        conn = sqlite3.connect(self.db_path)
        result = conn.execute(query).fetchone()
        return result is not None

    def get_user_profile(self, user_id):
        profile_path = f"/profiles/{user_id}.json"
        with open(profile_path, 'r') as f:
            return f.read()
""",
                        language="python",
                    )
                    analyze_btn1 = gr.Button("Analyze", size="sm")

                    # Example 2: Performance & Memory Issues
                    gr.Markdown("**2. Performance & Memory Issues**")
                    gr.Code(
                        """
import time
import threading
from collections import defaultdict

class DataProcessor:
    def __init__(self):
        self.cache = {}
        self.threads = []

    def process_large_dataset(self, data_list):
        for item in data_list:
            for other_item in data_list:
                if item == other_item:
                    self.cache[item] = other_item

        for i in range(100):
            thread = threading.Thread(target=self.background_task)
            self.threads.append(thread)
            thread.start()

    def background_task(self):
        while True:
            time.sleep(1)
            self.cache[time.time()] = "data"
""",
                        language="python",
                    )
                    analyze_btn2 = gr.Button("Analyze", size="sm")

                    # Example 3: Error Handling & Logging
                    gr.Markdown("**3. Error Handling & Logging**")
                    gr.Code(
                        """
import logging
import subprocess
import json

class FileManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def process_file(self, filepath):
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                return json.loads(content)
        except:
            pass

    def execute_system_command(self, command):
        try:
            result = subprocess.run(command, shell=True, capture_output=True)
            return result.stdout.decode()
        except:
            pass

    def delete_file(self, filepath):
        import os
        os.remove(filepath)
        return True
""",
                        language="python",
                    )
                    analyze_btn3 = gr.Button("Analyze", size="sm")

                    # Example 4: Concurrency & Thread Safety
                    gr.Markdown("**4. Concurrency & Thread Safety**")
                    gr.Code(
                        """
import threading
import time
from queue import Queue

shared_counter = 0
shared_data = []
data_queue = Queue()

class ThreadUnsafeManager:
    def __init__(self):
        self.local_counter = 0

    def increment_global_counter(self):
        global shared_counter
        temp = shared_counter
        time.sleep(0.001)
        shared_counter = temp + 1

    def add_to_shared_data(self, item):
        global shared_data
        shared_data.append(item)

    def process_queue_items(self):
        threads = []
        for i in range(10):
            thread = threading.Thread(target=self.worker, args=(i,))
            threads.append(thread)
            thread.start()
        return len(shared_data)
""",
                        language="python",
                    )
                    analyze_btn4 = gr.Button("Analyze", size="sm")

                    # Example 5: Code Quality & Maintainability
                    gr.Markdown("**5. Code Quality & Maintainability**")
                    gr.Code(
                        """
import requests
import hashlib
import base64

class APIClient:
    def __init__(self):
        self.api_key = "sk-1234567890abcdef"
        self.base_url = "https://api.example.com"
        self.session = requests.Session()

    def authenticate_user(self, username, password):
        hashed_password = hashlib.md5(password.encode()).hexdigest()

        response = self.session.post(
            f"{self.base_url}/auth",
            json={"username": username, "password": hashed_password}
        )
        return response.json()

    def get_sensitive_data(self, user_id):
        response = self.session.get(f"{self.base_url}/users/{user_id}/data")
        return response.json()

    def update_user_profile(self, user_id, data):
        response = self.session.put(
            f"{self.base_url}/users/{user_id}",
            json=data
        )
        return response.status_code == 200
""",
                        language="python",
                    )
                    analyze_btn5 = gr.Button("Analyze", size="sm")

                    # Function to get example code
                    def analyze_example(example_num):
                        examples = [
                            """import sqlite3
import os
from flask import Flask, request

app = Flask(__name__)
app.secret_key = "hardcoded_secret_key_123"

class UserService:
    def __init__(self):
        self.db_path = "users.db"

    def authenticate_user(self, username, password):
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        conn = sqlite3.connect(self.db_path)
        result = conn.execute(query).fetchone()
        return result is not None

    def get_user_profile(self, user_id):
        profile_path = f"/profiles/{user_id}.json"
        with open(profile_path, 'r') as f:
            return f.read()""",
                            """import time
import threading
from collections import defaultdict

class DataProcessor:
    def __init__(self):
        self.cache = {}
        self.threads = []

    def process_large_dataset(self, data_list):
        for item in data_list:
            for other_item in data_list:
                if item == other_item:
                    self.cache[item] = other_item

        for i in range(100):
            thread = threading.Thread(target=self.background_task)
            self.threads.append(thread)
            thread.start()

    def background_task(self):
        while True:
            time.sleep(1)
            self.cache[time.time()] = "data" """,
                            """import logging
import subprocess
import json

class FileManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def process_file(self, filepath):
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                return json.loads(content)
        except:
            pass

    def execute_system_command(self, command):
        try:
            result = subprocess.run(command, shell=True, capture_output=True)
            return result.stdout.decode()
        except:
            pass

    def delete_file(self, filepath):
        import os
        os.remove(filepath)
        return True""",
                            """import threading
import time
from queue import Queue

shared_counter = 0
shared_data = []
data_queue = Queue()

class ThreadUnsafeManager:
    def __init__(self):
        self.local_counter = 0

    def increment_global_counter(self):
        global shared_counter
        temp = shared_counter
        time.sleep(0.001)
        shared_counter = temp + 1

    def add_to_shared_data(self, item):
        global shared_data
        shared_data.append(item)

    def process_queue_items(self):
        threads = []
        for i in range(10):
            thread = threading.Thread(target=self.worker, args=(i,))
            threads.append(thread)
            thread.start()
        return len(shared_data)""",
                            """import requests
import hashlib
import base64

class APIClient:
    def __init__(self):
        self.api_key = "sk-1234567890abcdef"
        self.base_url = "https://api.example.com"
        self.session = requests.Session()

    def authenticate_user(self, username, password):
        hashed_password = hashlib.md5(password.encode()).hexdigest()

        response = self.session.post(
            f"{self.base_url}/auth",
            json={"username": username, "password": hashed_password}
        )
        return response.json()

    def get_sensitive_data(self, user_id):
        response = self.session.get(f"{self.base_url}/users/{user_id}/data")
        return response.json()

    def update_user_profile(self, user_id, data):
        response = self.session.put(
            f"{self.base_url}/users/{user_id}",
            json=data
        )
        return response.status_code == 200""",
                        ]
                        return examples[example_num - 1]

                    # Connect example buttons to input
                    analyze_btn1.click(lambda: analyze_example(1), outputs=msg)
                    analyze_btn2.click(lambda: analyze_example(2), outputs=msg)
                    analyze_btn3.click(lambda: analyze_example(3), outputs=msg)
                    analyze_btn4.click(lambda: analyze_example(4), outputs=msg)
                    analyze_btn5.click(lambda: analyze_example(5), outputs=msg)

                with gr.Tab("System Status"):
                    gr.Markdown("### System Status & Server Management")

                    # Server selection section
                    gr.Markdown("#### 🔧 Select Active Servers")
                    gr.Markdown(
                        "Choose which MCP servers to use for analysis. Only selected servers will be available to the agent."
                    )

                    # Create checkboxes for each server with tool info
                    server_checkboxes = {}
                    for server_key, server_config in client.servers.items():
                        is_connected = server_key in client.mcp_clients
                        is_enabled = server_key in client.enabled_servers

                        # Get tool count for this server
                        tool_count = 0
                        if is_connected:
                            try:
                                tools = client.get_server_tools(server_key)
                                tool_count = len(tools)
                            except Exception:
                                tool_count = 0

                        # Create tool list for display
                        tool_list = ""
                        if is_connected and tool_count > 0:
                            try:
                                tools = client.get_server_tools(server_key)
                                tool_names = [
                                    tool.name for tool in tools
                                ]  # Show all tools
                                tool_list = f"**{tool_count} tools:** {', '.join(tool_names)}"
                            except Exception:
                                tool_list = "Error loading tools"
                        elif is_connected:
                            tool_list = "No tools available"
                        else:
                            tool_list = "Server not connected"

                        checkbox = gr.Checkbox(
                            label=f"{server_config['name']} ({'🟢 Connected' if is_connected else '🔴 Disconnected'})",
                            value=is_enabled and is_connected,
                            interactive=is_connected,
                            info=f"URL: {server_config['url']}\n\n{tool_list}",
                        )
                        server_checkboxes[server_key] = checkbox

                    # Apply selection button
                    apply_btn = gr.Button(
                        "Apply Server Selection", variant="primary"
                    )

                    def update_server_selection(*checkbox_values):
                        """Update which servers are enabled based on checkbox selections."""
                        enabled_servers = []
                        for i, (server_key, checkbox) in enumerate(
                            server_checkboxes.items()
                        ):
                            if checkbox_values[i]:
                                enabled_servers.append(server_key)

                        # Log the server selection changes
                        print("🔧 Server selection updated:")
                        for (
                            server_key,
                            server_config,
                        ) in client.servers.items():
                            is_selected = server_key in enabled_servers
                            was_enabled = server_key in client.enabled_servers
                            if is_selected != was_enabled:
                                action = (
                                    "✅ Enabled"
                                    if is_selected
                                    else "❌ Disabled"
                                )
                                print(
                                    f"  {action} {server_config['name']} ({server_key})"
                                )

                        client.set_enabled_servers(enabled_servers)

                        return f"✅ Updated server selection. {len(enabled_servers)} servers enabled."

                    # Event handlers
                    apply_btn.click(
                        update_server_selection,
                        inputs=list(server_checkboxes.values()),
                        outputs=[],
                    )

                    # Auto-refresh functionality (placeholder - would need timer in real implementation)

        return demo, client

    except Exception as e:
        print(f"Error initializing client: {e}")
        return None, None


def main():
    """Main function to run the client."""
    demo, client = create_multi_server_interface()

    if demo:
        try:
            # Load configuration for launch settings
            config = load_config()
            gradio_config = config.get("gradio", {})

            # Launch the interface
            demo.launch(
                server_name=gradio_config.get("server_name", "127.0.0.1"),
                server_port=gradio_config.get("server_port", 7864),
                share=gradio_config.get("share", False),
                show_error=gradio_config.get("show_error", True),
            )
        except Exception as e:
            print(f"Failed to launch interface: {e}")
            print("Trying to launch on any available port...")
            try:
                demo.launch(share=False, show_error=True)
            except Exception as e2:
                print(f"Failed to launch interface on any port: {e2}")
        finally:
            # Cleanup on exit
            if client:
                client.disconnect()
    else:
        print(
            "Failed to create interface. Check your configuration and server status."
        )


if __name__ == "__main__":
    main()
