import json
import logging
import os
import subprocess
import sys

# Add the project root to the path to import config_loader
sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ),
)

import gradio as gr

from config_loader import get_config_loader

# Load configuration
config_loader = get_config_loader()
server_config = config_loader.get_server_config("git_repo_analysis")
logging_config = config_loader.get_logging_config()

# Configure logging
log_file = logging_config.get("file", "mcp_servers.log")
log_level = getattr(logging, logging_config.get("level", "INFO"))
log_format = logging_config.get(
    "format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

file_handler = logging.FileHandler(log_file)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)  # Only errors to console

logging.basicConfig(
    level=log_level,
    format=log_format,
    handlers=[file_handler, console_handler],
)
logger = logging.getLogger(__name__)


def git_status(file_path: str) -> str:
    """
    Get the git status of a specific file.

    Args:
        file_path (str): Path to the file to check git status

    Returns:
        str: JSON string with git status information
    """
    logger.info("Starting git_status function")
    logger.info(f"Input file_path: {file_path}")

    try:
        # Check if file exists
        if not os.path.exists(file_path):
            return json.dumps({"error": f"File {file_path} does not exist"})

        # Get the directory containing the file
        file_dir = os.path.dirname(os.path.abspath(file_path))

        # Check if it's a git repository
        if not os.path.exists(os.path.join(file_dir, ".git")):
            return json.dumps(
                {"error": f"Directory {file_dir} is not a git repository"}
            )

        # Get relative path from git root
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=file_dir,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            return json.dumps({"error": "Failed to get git root directory"})

        git_root = result.stdout.strip()
        relative_path = os.path.relpath(file_path, git_root)

        # Get git status
        status_result = subprocess.run(
            ["git", "status", "--porcelain", relative_path],
            cwd=git_root,
            capture_output=True,
            text=True,
        )

        if status_result.returncode != 0:
            return json.dumps({"error": "Failed to get git status"})

        status_output = status_result.stdout.strip()

        # Parse status
        if not status_output:
            status = "tracked"
            message = "File is tracked and up to date"
        else:
            status_code = status_output[:2]
            if status_code == "M ":
                status = "modified"
                message = "File has been modified"
            elif status_code == " M":
                status = "modified"
                message = "File has unstaged changes"
            elif status_code == "A ":
                status = "added"
                message = "File has been added to staging"
            elif status_code == "??":
                status = "untracked"
                message = "File is untracked"
            elif status_code == "D ":
                status = "deleted"
                message = "File has been deleted"
            else:
                status = "unknown"
                message = f"Unknown status: {status_code}"

        # Get last commit info
        log_result = subprocess.run(
            [
                "git",
                "log",
                "-1",
                "--format=%H|%an|%ad|%s",
                "--date=short",
                "--",
                relative_path,
            ],
            cwd=git_root,
            capture_output=True,
            text=True,
        )

        last_commit = None
        if log_result.returncode == 0 and log_result.stdout.strip():
            commit_parts = log_result.stdout.strip().split("|")
            if len(commit_parts) == 4:
                last_commit = {
                    "hash": commit_parts[0][:8],
                    "author": commit_parts[1],
                    "date": commit_parts[2],
                    "message": commit_parts[3],
                }

        status_result_dict = {
            "file_path": file_path,
            "relative_path": relative_path,
            "status": status,
            "message": message,
            "status_code": status_output[:2] if status_output else None,
            "last_commit": last_commit,
            "git_root": git_root,
        }

        logger.info(
            f"Git status completed - Status: {status}, Message: {message}"
        )
        logger.info("git_status function completed successfully")
        return json.dumps(status_result_dict, indent=2)

    except Exception as e:
        logger.error(f"Error in git_status: {str(e)}")
        logger.info("git_status function completed with error")
        return json.dumps({"error": f"Failed to get git status: {str(e)}"})


def git_add(file_path: str) -> str:
    """
    Add a file to git staging area.

    Args:
        file_path (str): Path to the file to add

    Returns:
        str: JSON string with add operation result
    """
    logger.info("Starting git_add function")
    logger.info(f"Input file_path: {file_path}")

    try:
        # Check if file exists
        if not os.path.exists(file_path):
            return json.dumps({"error": f"File {file_path} does not exist"})

        # Get the directory containing the file
        file_dir = os.path.dirname(os.path.abspath(file_path))

        # Check if it's a git repository
        if not os.path.exists(os.path.join(file_dir, ".git")):
            return json.dumps(
                {"error": f"Directory {file_dir} is not a git repository"}
            )

        # Get relative path from git root
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=file_dir,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            return json.dumps({"error": "Failed to get git root directory"})

        git_root = result.stdout.strip()
        relative_path = os.path.relpath(file_path, git_root)

        # Add file to staging
        add_result = subprocess.run(
            ["git", "add", relative_path],
            cwd=git_root,
            capture_output=True,
            text=True,
        )

        if add_result.returncode != 0:
            return json.dumps(
                {"error": f"Failed to add file: {add_result.stderr}"}
            )

        # Get updated status
        status_result = subprocess.run(
            ["git", "status", "--porcelain", relative_path],
            cwd=git_root,
            capture_output=True,
            text=True,
        )

        status_output = status_result.stdout.strip()

        add_result_dict = {
            "file_path": file_path,
            "relative_path": relative_path,
            "action": "added",
            "success": True,
            "message": f"File {relative_path} has been added to staging",
            "current_status": status_output[:2] if status_output else None,
        }

        logger.info(
            f"Git add completed - File: {relative_path}, Success: True"
        )
        logger.info("git_add function completed successfully")
        return json.dumps(add_result_dict, indent=2)

    except Exception as e:
        logger.error(f"Error in git_add: {str(e)}")
        logger.info("git_add function completed with error")
        return json.dumps({"error": f"Failed to add file: {str(e)}"})


def git_commit(file_path: str, commit_message: str) -> str:
    """
    Commit changes for a specific file.

    Args:
        file_path (str): Path to the file to commit
        commit_message (str): Commit message

    Returns:
        str: JSON string with commit operation result
    """
    logger.info("Starting git_commit function")
    logger.info(
        f"Input file_path: {file_path}, commit_message: {commit_message[:50]}..."
    )

    try:
        # Check if file exists
        if not os.path.exists(file_path):
            return json.dumps({"error": f"File {file_path} does not exist"})

        # Get the directory containing the file
        file_dir = os.path.dirname(os.path.abspath(file_path))

        # Check if it's a git repository
        if not os.path.exists(os.path.join(file_dir, ".git")):
            return json.dumps(
                {"error": f"Directory {file_dir} is not a git repository"}
            )

        # Get relative path from git root
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=file_dir,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            return json.dumps({"error": "Failed to get git root directory"})

        git_root = result.stdout.strip()
        relative_path = os.path.relpath(file_path, git_root)

        # Check if there are staged changes
        status_result = subprocess.run(
            ["git", "status", "--porcelain", relative_path],
            cwd=git_root,
            capture_output=True,
            text=True,
        )

        if status_result.returncode != 0:
            return json.dumps({"error": "Failed to check git status"})

        status_output = status_result.stdout.strip()

        if not status_output:
            return json.dumps({"error": "No changes to commit for this file"})

        # Check if file is staged (status starts with A, M, D)
        if not any(
            status_output.startswith(code) for code in ["A ", "M ", "D "]
        ):
            return json.dumps(
                {"error": "File is not staged. Use git_add first."}
            )

        # Commit the changes
        commit_result = subprocess.run(
            ["git", "commit", "-m", commit_message, "--", relative_path],
            cwd=git_root,
            capture_output=True,
            text=True,
        )

        if commit_result.returncode != 0:
            return json.dumps(
                {"error": f"Failed to commit: {commit_result.stderr}"}
            )

        # Get the commit hash
        hash_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=git_root,
            capture_output=True,
            text=True,
        )

        commit_hash = (
            hash_result.stdout.strip()[:8]
            if hash_result.returncode == 0
            else "unknown"
        )

        commit_result_dict = {
            "file_path": file_path,
            "relative_path": relative_path,
            "action": "committed",
            "success": True,
            "message": "Changes committed successfully",
            "commit_hash": commit_hash,
            "commit_message": commit_message,
        }

        logger.info(
            f"Git commit completed - File: {relative_path}, Hash: {commit_hash}"
        )
        logger.info("git_commit function completed successfully")
        return json.dumps(commit_result_dict, indent=2)

    except Exception as e:
        logger.error(f"Error in git_commit: {str(e)}")
        logger.info("git_commit function completed with error")
        return json.dumps({"error": f"Failed to commit: {str(e)}"})


def git_diff(file_path: str, staged: bool = False) -> str:
    """
    Get git diff for a specific file.

    Args:
        file_path (str): Path to the file to get diff for
        staged (bool): Whether to show staged changes (True) or unstaged changes (False)

    Returns:
        str: JSON string with diff information
    """
    logger.info("Starting git_diff function")
    logger.info(f"Input file_path: {file_path}, staged: {staged}")

    try:
        # Check if file exists
        if not os.path.exists(file_path):
            return json.dumps({"error": f"File {file_path} does not exist"})

        # Get the directory containing the file
        file_dir = os.path.dirname(os.path.abspath(file_path))

        # Check if it's a git repository
        if not os.path.exists(os.path.join(file_dir, ".git")):
            return json.dumps(
                {"error": f"Directory {file_dir} is not a git repository"}
            )

        # Get relative path from git root
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=file_dir,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            return json.dumps({"error": "Failed to get git root directory"})

        git_root = result.stdout.strip()
        relative_path = os.path.relpath(file_path, git_root)

        # Build git diff command
        diff_cmd = ["git", "diff"]
        if staged:
            diff_cmd.append("--cached")
        diff_cmd.extend(["--", relative_path])

        # Get diff
        diff_result = subprocess.run(
            diff_cmd, cwd=git_root, capture_output=True, text=True
        )

        if diff_result.returncode != 0:
            return json.dumps(
                {"error": f"Failed to get diff: {diff_result.stderr}"}
            )

        diff_output = diff_result.stdout.strip()

        # Parse diff statistics
        stat_cmd = ["git", "diff", "--stat"]
        if staged:
            stat_cmd.append("--cached")
        stat_cmd.extend(["--", relative_path])

        stat_result = subprocess.run(
            stat_cmd, cwd=git_root, capture_output=True, text=True
        )

        stat_output = (
            stat_result.stdout.strip() if stat_result.returncode == 0 else ""
        )

        # Count lines added/removed
        lines_added = 0
        lines_removed = 0

        for line in diff_output.split("\n"):
            if line.startswith("+") and not line.startswith("+++"):
                lines_added += 1
            elif line.startswith("-") and not line.startswith("---"):
                lines_removed += 1

        diff_result_dict = {
            "file_path": file_path,
            "relative_path": relative_path,
            "staged": staged,
            "diff": diff_output if diff_output else "No changes found",
            "statistics": stat_output,
            "lines_added": lines_added,
            "lines_removed": lines_removed,
            "has_changes": bool(diff_output),
        }

        logger.info(
            f"Git diff completed - File: {relative_path}, Lines added: {lines_added}, Lines removed: {lines_removed}"
        )
        logger.info("git_diff function completed successfully")
        return json.dumps(diff_result_dict, indent=2)

    except Exception as e:
        logger.error(f"Error in git_diff: {str(e)}")
        logger.info("git_diff function completed with error")
        return json.dumps({"error": f"Failed to get diff: {str(e)}"})


def git_log(file_path: str, limit: int = 5) -> str:
    """
    Get git log for a specific file.

    Args:
        file_path (str): Path to the file to get log for
        limit (int): Maximum number of commits to show

    Returns:
        str: JSON string with log information
    """
    logger.info("Starting git_log function")
    logger.info(f"Input file_path: {file_path}, limit: {limit}")

    try:
        # Check if file exists
        if not os.path.exists(file_path):
            return json.dumps({"error": f"File {file_path} does not exist"})

        # Get the directory containing the file
        file_dir = os.path.dirname(os.path.abspath(file_path))

        # Check if it's a git repository
        if not os.path.exists(os.path.join(file_dir, ".git")):
            return json.dumps(
                {"error": f"Directory {file_dir} is not a git repository"}
            )

        # Get relative path from git root
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=file_dir,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            return json.dumps({"error": "Failed to get git root directory"})

        git_root = result.stdout.strip()
        relative_path = os.path.relpath(file_path, git_root)

        # Get git log
        log_result = subprocess.run(
            [
                "git",
                "log",
                f"-{limit}",
                "--format=%H|%an|%ad|%s",
                "--date=short",
                "--",
                relative_path,
            ],
            cwd=git_root,
            capture_output=True,
            text=True,
        )

        if log_result.returncode != 0:
            return json.dumps(
                {"error": f"Failed to get git log: {log_result.stderr}"}
            )

        log_output = log_result.stdout.strip()

        commits = []
        if log_output:
            for line in log_output.split("\n"):
                if line.strip():
                    parts = line.split("|")
                    if len(parts) == 4:
                        commits.append(
                            {
                                "hash": parts[0][:8],
                                "full_hash": parts[0],
                                "author": parts[1],
                                "date": parts[2],
                                "message": parts[3],
                            }
                        )

        log_result_dict = {
            "file_path": file_path,
            "relative_path": relative_path,
            "limit": limit,
            "commits": commits,
            "total_commits": len(commits),
        }

        logger.info(
            f"Git log completed - File: {relative_path}, Commits found: {len(commits)}"
        )
        logger.info("git_log function completed successfully")
        return json.dumps(log_result_dict, indent=2)

    except Exception as e:
        logger.error(f"Error in git_log: {str(e)}")
        logger.info("git_log function completed with error")
        return json.dumps({"error": f"Failed to get git log: {str(e)}"})


# Create individual interfaces for each function
git_status_demo = gr.Interface(
    fn=git_status,
    inputs=gr.Textbox(
        placeholder="Enter file path to check git status...",
        label="File Path",
        lines=2,
    ),
    outputs=gr.JSON(label="Git Status Result"),
    title="Git Status",
    description="Check the git status of a specific file in a git repository.",
    examples=[
        ["server/git_server/git_server.py"],
        ["README.md"],
        ["requirements.txt"],
        ["client/basic_client/client.py"],
    ],
)

git_add_demo = gr.Interface(
    fn=git_add,
    inputs=gr.Textbox(
        placeholder="Enter file path to add to git...",
        label="File Path",
        lines=2,
    ),
    outputs=gr.JSON(label="Git Add Result"),
    title="Git Add",
    description="Add a file to the git staging area.",
    examples=[
        ["new_file.py"],
        ["modified_file.py"],
        ["server/git_server/test_client.py"],
    ],
)

git_commit_demo = gr.Interface(
    fn=git_commit,
    inputs=[
        gr.Textbox(
            placeholder="Enter file path to commit...",
            label="File Path",
            lines=2,
        ),
        gr.Textbox(
            placeholder="Enter commit message...",
            label="Commit Message",
            lines=2,
        ),
    ],
    outputs=gr.JSON(label="Git Commit Result"),
    title="Git Commit",
    description="Commit changes for a specific file with a custom message.",
    examples=[
        ["modified_file.py", "Fix bug in data processing"],
        ["new_feature.py", "Add new feature"],
        ["README.md", "Update documentation"],
    ],
)

git_diff_demo = gr.Interface(
    fn=git_diff,
    inputs=[
        gr.Textbox(
            placeholder="Enter file path to get diff...",
            label="File Path",
            lines=2,
        ),
        gr.Checkbox(label="Show Staged Changes", value=False),
    ],
    outputs=gr.JSON(label="Git Diff Result"),
    title="Git Diff",
    description="Get git diff for a specific file (staged or unstaged changes).",
    examples=[
        ["server/git_server/git_server.py", False],
        ["modified_file.py", True],
        ["README.md", False],
    ],
)

git_log_demo = gr.Interface(
    fn=git_log,
    inputs=[
        gr.Textbox(
            placeholder="Enter file path to get log...",
            label="File Path",
            lines=2,
        ),
        gr.Slider(minimum=1, maximum=20, value=5, step=1, label="Log Limit"),
    ],
    outputs=gr.JSON(label="Git Log Result"),
    title="Git Log",
    description="Get git log for a specific file with configurable commit limit.",
    examples=[
        ["server/git_server/git_server.py", 5],
        ["README.md", 10],
        ["requirements.txt", 3],
    ],
)

# Create tabbed interface
demo = gr.TabbedInterface(
    [
        git_status_demo,
        git_add_demo,
        git_commit_demo,
        git_diff_demo,
        git_log_demo,
    ],
    ["Git Status", "Git Add", "Git Commit", "Git Diff", "Git Log"],
    title="Git Operations Server",
)

# Launch the interface and MCP server
if __name__ == "__main__":
    port = server_config["port"]
    logger.info(f"Starting {server_config['name']}")
    logger.info(f"Launching Gradio interface on port {port}")
    try:
        demo.launch(server_name="0.0.0.0", server_port=port, mcp_server=True)
        logger.info(f"{server_config['name']} started successfully")
    except Exception as e:
        logger.error(f"Failed to start {server_config['name']}: {str(e)}")
        raise
