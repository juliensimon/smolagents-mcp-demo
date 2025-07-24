"""MCP Code Retriever Server for fetching and loading code from URLs and local files via Gradio interface."""

import hashlib
import json
import logging
import os
import sys
from urllib.parse import urlparse

# Add the project root to the path to import config_loader
sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ),
)

import gradio as gr  # noqa: E402
import requests  # noqa: E402

from config_loader import get_config_loader  # noqa: E402

# Load configuration
config_loader = get_config_loader()
server_config = config_loader.get_server_config("code_retrieval")
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


def retrieve_url(url: str) -> str:
    """
    Retrieve content from a URL and return it with metadata.

    This function fetches the content of a web resource from the provided URL.
    It handles various HTTP scenarios including redirects, timeouts, and errors.
    The function is designed to work with text-based content (HTML, JSON, XML,
    plain text, code files, etc.) and automatically handles encoding.

    Args:
        url (str): The complete URL to retrieve content from. Must include the
                  protocol (http:// or https://) and be a valid URL format.
                  Examples: "https://api.github.com/users/octocat",
                           "https://raw.githubusercontent.com/user/repo/main/README.md"

    Returns:
        str: A JSON string containing the retrieval result with the following structure:

        On success:
        {
            "success": true,
            "url": "original_url",
            "content": "retrieved_content_as_string",
            "content_length": 1234,
            "content_hash": "md5_hash_of_content",
            "content_type": "text/html",
            "encoding": "utf-8",
            "status_code": 200
        }

        On failure:
        {
            "success": false,
            "error": "description_of_error",
            "url": "original_url",
            "status_code": 404  // if applicable
        }

    Raises:
        No exceptions are raised - all errors are returned in the JSON response.

    Examples:
        >>> result = retrieve_url("https://httpbin.org/json")
        >>> data = json.loads(result)
        >>> if data["success"]:
        ...     print(f"Retrieved {data['content_length']} characters")
        ...     print(f"Content type: {data['content_type']}")
        ... else:
        ...     print(f"Error: {data['error']}")

    Notes:
        - Uses a 30-second timeout for requests
        - Follows HTTP redirects automatically
        - Includes a user-agent header to avoid blocking
        - Calculates MD5 hash of content for integrity verification
        - Handles common HTTP status codes and network errors
    """
    logger.info("Retrieving content from URL: %s", url)

    try:
        # Parse URL
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return json.dumps(
                {"success": False, "error": "Invalid URL format", "url": url}
            )

        # Retrieve the content
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        response = requests.get(
            url, headers=headers, timeout=30, allow_redirects=True
        )

        if response.status_code == 200:
            content = response.text
            content_length = len(content)
            content_hash = hashlib.md5(content.encode("utf-8")).hexdigest()

            result = {
                "success": True,
                "url": url,
                "content": content,
                "content_length": content_length,
                "content_hash": content_hash,
                "content_type": response.headers.get(
                    "content-type", "unknown"
                ),
                "encoding": response.encoding,
                "status_code": response.status_code,
            }

            logger.info(
                f"Successfully retrieved content from {url} - {content_length} characters"
            )
            return json.dumps(result, indent=2)
        else:
            logger.error(
                "HTTP error %d for URL: %s", response.status_code, url
            )
            return json.dumps(
                {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.reason}",
                    "url": url,
                    "status_code": response.status_code,
                }
            )

    except requests.exceptions.Timeout:
        logger.error("Timeout error for URL: %s", url)
        return json.dumps(
            {"success": False, "error": "Request timeout", "url": url}
        )
    except requests.exceptions.ConnectionError:
        logger.error("Connection error for URL: %s", url)
        return json.dumps(
            {"success": False, "error": "Connection error", "url": url}
        )
    except (requests.exceptions.RequestException, ValueError, TypeError) as e:
        logger.error("Error retrieving URL %s: %s", url, str(e))
        return json.dumps(
            {
                "success": False,
                "error": f"Request failed: {str(e)}",
                "url": url,
            }
        )


def load_local_file(file_path: str) -> str:
    """
    Load content from a local file on the server filesystem.

    This function reads the contents of a file from the local filesystem and returns
    it along with metadata about the file. It's designed to work with text-based files
    and handles various file system scenarios including missing files, permission issues,
    and encoding problems.

    Args:
        file_path (str): The absolute or relative path to the file on the server's
                        filesystem. Can be a relative path from the current working
                        directory or an absolute path.
                        Examples: "/etc/hosts", "./config.json", "data/input.txt"

    Returns:
        str: A JSON string containing the file loading result with the following structure:

        On success:
        {
            "success": true,
            "file_path": "original_file_path",
            "content": "file_content_as_string",
            "content_length": 1234,
            "content_hash": "md5_hash_of_content",
            "file_size_bytes": 1234,
            "last_modified": 1640995200.0,
            "file_extension": ".txt"
        }

        On failure:
        {
            "success": false,
            "error": "description_of_error",
            "file_path": "original_file_path"
        }

    Raises:
        No exceptions are raised - all errors are returned in the JSON response.

    Examples:
        >>> result = load_local_file("/etc/hosts")
        >>> data = json.loads(result)
        >>> if data["success"]:
        ...     print(f"Loaded {data['content_length']} characters from {data['file_path']}")
        ...     print(f"File size: {data['file_size_bytes']} bytes")
        ... else:
        ...     print(f"Error: {data['error']}")

    Notes:
        - Attempts to read files as UTF-8 encoded text
        - Calculates MD5 hash of content for integrity verification
        - Returns file system metadata (size, modification time)
        - Handles common file system errors (missing files, permissions, etc.)
        - File extension is extracted from the path if present
        - Modification time is returned as Unix timestamp
    """
    logger.info("Loading local file: %s", file_path)

    try:
        # Check if file exists
        if not os.path.exists(file_path):
            return json.dumps(
                {
                    "success": False,
                    "error": "File does not exist",
                    "file_path": file_path,
                }
            )

        # Check if it's a file (not a directory)
        if not os.path.isfile(file_path):
            return json.dumps(
                {
                    "success": False,
                    "error": "Path is not a file",
                    "file_path": file_path,
                }
            )

        # Read file content
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        content_length = len(content)
        content_hash = hashlib.md5(content.encode("utf-8")).hexdigest()

        # Get file stats
        file_stats = os.stat(file_path)

        result = {
            "success": True,
            "file_path": file_path,
            "content": content,
            "content_length": content_length,
            "content_hash": content_hash,
            "file_size_bytes": file_stats.st_size,
            "last_modified": file_stats.st_mtime,
            "file_extension": (
                os.path.splitext(file_path)[1] if "." in file_path else None
            ),
        }

        logger.info(
            f"Successfully loaded local file {file_path} - {content_length} characters"
        )
        return json.dumps(result, indent=2)

    except PermissionError:
        logger.error("Permission denied for file: %s", file_path)
        return json.dumps(
            {
                "success": False,
                "error": "Permission denied",
                "file_path": file_path,
            }
        )
    except UnicodeDecodeError:
        logger.error("Unicode decode error for file: %s", file_path)
        return json.dumps(
            {
                "success": False,
                "error": "File encoding not supported (try binary file)",
                "file_path": file_path,
            }
        )
    except (OSError, IOError, ValueError) as e:
        logger.error("Error loading local file %s: %s", file_path, str(e))
        return json.dumps(
            {
                "success": False,
                "error": f"Failed to load file: {str(e)}",
                "file_path": file_path,
            }
        )


# Create Gradio interfaces
url_retrieval_demo = gr.Interface(
    fn=retrieve_url,
    inputs=gr.Textbox(
        placeholder="Enter URL to retrieve content from (e.g., https://example.com/file.txt)",
        label="URL",
        lines=2,
    ),
    outputs=gr.JSON(label="URL Retrieval Result"),
    title="URL Content Retrieval",
    description="Retrieve content from any accessible URL.",
    examples=[
        ["https://raw.githubusercontent.com/gradio-app/gradio/main/README.md"],
        ["https://httpbin.org/json"],
        ["https://raw.githubusercontent.com/python/cpython/main/README.md"],
    ],
)

local_file_demo = gr.Interface(
    fn=load_local_file,
    inputs=gr.Textbox(
        placeholder="Enter local file path (e.g., /path/to/file.txt)",
        label="File Path",
        lines=2,
    ),
    outputs=gr.JSON(label="Local File Result"),
    title="Local File Loading",
    description="Load content from a local file on the server.",
    examples=[
        ["/etc/hosts"],
        ["./README.md"],
        ["/tmp/test.txt"],
    ],
)

# Create tabbed interface
demo = gr.TabbedInterface(
    [url_retrieval_demo, local_file_demo],
    ["URL Retrieval", "Local File"],
    title="MCP Server - Code & File Retrieval",
)

# Launch the interface and MCP server
if __name__ == "__main__":
    port = server_config["port"]
    logger.info("Starting %s", server_config["name"])
    logger.info("Launching Gradio interface on port %s", port)
    try:
        demo.launch(server_port=port, mcp_server=True)
        logger.info("%s started successfully", server_config["name"])
    except (OSError, RuntimeError, ValueError) as e:
        logger.error("Failed to start %s: %s", server_config["name"], str(e))
        raise
