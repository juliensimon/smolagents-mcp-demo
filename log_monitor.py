#!/usr/bin/env python3
"""
Log monitor that filters out ListToolsRequest messages and shows tool calls
"""

import os
import time


def monitor_logs(log_file="mcp_servers.log"):
    """Monitor log file and filter out ListToolsRequest messages."""

    if not os.path.exists(log_file):
        print(
            f"Log file {log_file} not found. Waiting for it to be created..."
        )
        while not os.path.exists(log_file):
            time.sleep(1)

    print(f"🔍 Monitoring {log_file} for tool calls...")
    print("📝 Filtering out ListToolsRequest messages")
    print("=" * 60)

    # Track the last position in the file
    last_position = 0

    try:
        while True:
            with open(log_file, "r") as f:
                f.seek(last_position)
                new_lines = f.readlines()
                last_position = f.tell()

                for line in new_lines:
                    # Skip ListToolsRequest messages
                    if (
                        "ListToolsRequest" in line
                        or "Processing request of type" in line
                    ):
                        continue

                    # Show tool-related messages
                    if any(
                        keyword in line.lower()
                        for keyword in ["tool", "call", "result"]
                    ):
                        print(f"🔧 {line.strip()}")
                    elif "ERROR" in line or "WARNING" in line:
                        print(f"⚠️  {line.strip()}")
                    elif (
                        "INFO" in line
                        and "mcp.server.lowlevel.server" not in line
                    ):
                        print(f"ℹ️  {line.strip()}")

            time.sleep(0.5)  # Check every 500ms

    except KeyboardInterrupt:
        print("\n👋 Log monitoring stopped")


if __name__ == "__main__":
    monitor_logs()
