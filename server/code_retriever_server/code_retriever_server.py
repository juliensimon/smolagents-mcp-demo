import hashlib
import json
import logging
import mimetypes
import os
import sys
import time
from typing import Any, Dict
from urllib.parse import urlparse

import gradio as gr
import requests

# Add the project root to the path to import config_loader
sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ),
)

from config_loader import get_config_loader

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


def validate_url(url: str) -> Dict[str, Any]:
    """
    Validate if the provided URL is accessible and returns file information.

    Args:
        url (str): The URL to validate

    Returns:
        dict: JSON string with validation results
    """
    logger.info("Starting validate_url function")
    logger.info(f"Input url: {url}")

    try:
        # Parse URL
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return json.dumps(
                {"valid": False, "error": "Invalid URL format", "url": url}
            )

        # Check if URL is accessible
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        response = requests.head(
            url, headers=headers, timeout=10, allow_redirects=True
        )

        if response.status_code == 200:
            content_type = response.headers.get("content-type", "unknown")
            content_length = response.headers.get("content-length", "unknown")
            last_modified = response.headers.get("last-modified", "unknown")

            # Try to determine file extension
            file_extension = None
            if "content-type" in response.headers:
                file_extension = mimetypes.guess_extension(
                    content_type.split(";")[0]
                )

            result = {
                "valid": True,
                "url": url,
                "content_type": content_type,
                "content_length": content_length,
                "last_modified": last_modified,
                "file_extension": file_extension,
                "status_code": response.status_code,
            }
            logger.info(
                f"URL validation completed - Valid: True, Status: {response.status_code}"
            )
            logger.info("validate_url function completed successfully")
            return json.dumps(result)
        else:
            result = {
                "valid": False,
                "error": f"HTTP {response.status_code}: {response.reason}",
                "url": url,
                "status_code": response.status_code,
            }
            logger.info(
                f"URL validation completed - Valid: False, Status: {response.status_code}"
            )
            logger.info("validate_url function completed successfully")
            return json.dumps(result)

    except requests.exceptions.Timeout:
        logger.error(f"Timeout error in validate_url: {url}")
        logger.info("validate_url function completed with error")
        return json.dumps(
            {"valid": False, "error": "Request timeout", "url": url}
        )
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error in validate_url: {url}")
        logger.info("validate_url function completed with error")
        return json.dumps(
            {"valid": False, "error": "Connection error", "url": url}
        )
    except requests.exceptions.RequestException as e:
        logger.error(f"Request exception in validate_url: {str(e)}")
        logger.info("validate_url function completed with error")
        return json.dumps(
            {"valid": False, "error": f"Request failed: {str(e)}", "url": url}
        )
    except Exception as e:
        logger.error(f"Unexpected error in validate_url: {str(e)}")
        logger.info("validate_url function completed with error")
        return json.dumps(
            {
                "valid": False,
                "error": f"Unexpected error: {str(e)}",
                "url": url,
            }
        )


def retrieve_file_content(url: str, include_metadata: bool = True) -> str:
    """
    Retrieve the content of a file from an HTTP server.

    Args:
        url (str): The URL of the file to retrieve
        include_metadata (bool): Whether to include metadata in the response

    Returns:
        str: JSON string with file content and metadata
    """
    logger.info("Starting retrieve_file_content function")
    logger.info(f"Input url: {url}, include_metadata: {include_metadata}")

    try:
        # Validate URL first
        validation_result = json.loads(validate_url(url))
        if not validation_result.get("valid", False):
            return json.dumps(
                {
                    "success": False,
                    "error": validation_result.get(
                        "error", "URL validation failed"
                    ),
                    "url": url,
                }
            )

        # Retrieve the file
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        start_time = time.time()
        response = requests.get(
            url, headers=headers, timeout=30, allow_redirects=True
        )
        download_time = time.time() - start_time

        if response.status_code == 200:
            content = response.text
            content_length = len(content)

            # Calculate content hash
            content_hash = hashlib.md5(content.encode("utf-8")).hexdigest()

            result = {
                "success": True,
                "url": url,
                "content": content,
                "content_length": content_length,
                "content_hash": content_hash,
                "download_time": round(download_time, 3),
                "encoding": response.encoding,
            }

            if include_metadata:
                result.update(
                    {
                        "content_type": response.headers.get(
                            "content-type", "unknown"
                        ),
                        "last_modified": response.headers.get(
                            "last-modified", "unknown"
                        ),
                        "etag": response.headers.get("etag", "unknown"),
                        "status_code": response.status_code,
                    }
                )

            logger.info(
                f"File retrieval completed - Content length: {content_length}, Download time: {download_time:.3f}s"
            )
            logger.info(
                "retrieve_file_content function completed successfully"
            )
            return json.dumps(result, indent=2)
        else:
            logger.error(
                f"HTTP error in retrieve_file_content: {response.status_code}"
            )
            logger.info("retrieve_file_content function completed with error")
            return json.dumps(
                {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.reason}",
                    "url": url,
                    "status_code": response.status_code,
                }
            )

    except requests.exceptions.Timeout:
        logger.error(f"Timeout error in retrieve_file_content: {url}")
        logger.info("retrieve_file_content function completed with error")
        return json.dumps(
            {"success": False, "error": "Request timeout", "url": url}
        )
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error in retrieve_file_content: {url}")
        logger.info("retrieve_file_content function completed with error")
        return json.dumps(
            {"success": False, "error": "Connection error", "url": url}
        )
    except requests.exceptions.RequestException as e:
        logger.error(f"Request exception in retrieve_file_content: {str(e)}")
        logger.info("retrieve_file_content function completed with error")
        return json.dumps(
            {
                "success": False,
                "error": f"Request failed: {str(e)}",
                "url": url,
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error in retrieve_file_content: {str(e)}")
        logger.info("retrieve_file_content function completed with error")
        return json.dumps(
            {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "url": url,
            }
        )


def analyze_file_content(content: str, file_type: str = "auto") -> str:
    """
    Analyze the content of a retrieved file.

    Args:
        content (str): The file content to analyze
        file_type (str): The type of file (auto, text, code, json, xml, etc.)

    Returns:
        str: JSON string with analysis results
    """
    logger.info("Starting analyze_file_content function")
    logger.info(
        f"Input content length: {len(content)} characters, file_type: {file_type}"
    )

    try:
        analysis = {
            "file_size": len(content),
            "line_count": len(content.splitlines()),
            "word_count": len(content.split()),
            "character_count": len(content),
            "non_whitespace_count": len(
                content.replace(" ", "").replace("\n", "").replace("\t", "")
            ),
            "file_type_detected": "unknown",
        }

        # Auto-detect file type if not specified
        if file_type == "auto":
            lines = content.splitlines()
            first_line = lines[0] if lines else ""

            # Detect common file types
            if content.strip().startswith("{") and content.strip().endswith(
                "}"
            ):
                analysis["file_type_detected"] = "json"
            elif content.strip().startswith("<") and "<?xml" in first_line:
                analysis["file_type_detected"] = "xml"
            elif content.strip().startswith(
                "<!DOCTYPE"
            ) or content.strip().startswith("<html"):
                analysis["file_type_detected"] = "html"
            elif any(
                keyword in first_line.lower()
                for keyword in ["#!/", "python", "import ", "def ", "class "]
            ):
                analysis["file_type_detected"] = "python"
            elif any(
                keyword in first_line.lower()
                for keyword in ["function", "var ", "const ", "let ", "//"]
            ):
                analysis["file_type_detected"] = "javascript"
            elif any(
                keyword in first_line.lower()
                for keyword in ["package ", "import ", "public class"]
            ):
                analysis["file_type_detected"] = "java"
            elif any(
                keyword in first_line.lower()
                for keyword in ["#include", "int main", "void main"]
            ):
                analysis["file_type_detected"] = "c"
            elif any(
                keyword in first_line.lower()
                for keyword in ["using ", "namespace ", "class "]
            ):
                analysis["file_type_detected"] = "cpp"
            elif any(
                keyword in first_line.lower()
                for keyword in ["require", "module.exports", "function"]
            ):
                analysis["file_type_detected"] = "nodejs"
            else:
                analysis["file_type_detected"] = "text"
        else:
            analysis["file_type_detected"] = file_type

        # Additional analysis based on detected type
        if analysis["file_type_detected"] == "json":
            try:
                json.loads(content)
                analysis["json_valid"] = True
            except json.JSONDecodeError as e:
                analysis["json_valid"] = False
                analysis["json_error"] = str(e)

        elif analysis["file_type_detected"] in [
            "python",
            "javascript",
            "java",
            "c",
            "cpp",
        ]:
            # Code analysis
            lines = content.splitlines()
            analysis["code_lines"] = len(
                [
                    line
                    for line in lines
                    if line.strip()
                    and not line.strip().startswith("//")
                    and not line.strip().startswith("#")
                ]
            )
            analysis["comment_lines"] = len(
                [
                    line
                    for line in lines
                    if line.strip().startswith("//")
                    or line.strip().startswith("#")
                ]
            )
            analysis["blank_lines"] = len(
                [line for line in lines if not line.strip()]
            )

            # Count functions/classes (simple detection)
            function_count = (
                content.count("def ")
                + content.count("function ")
                + content.count("public ")
                + content.count("private ")
            )
            class_count = content.count("class ")
            analysis["function_count"] = function_count
            analysis["class_count"] = class_count

        # Calculate readability metrics
        if analysis["word_count"] > 0:
            analysis["avg_words_per_line"] = round(
                analysis["word_count"] / analysis["line_count"], 2
            )
            analysis["avg_chars_per_word"] = round(
                analysis["character_count"] / analysis["word_count"], 2
            )

        logger.info(
            f"File content analysis completed - File type: {analysis['file_type_detected']}, Lines: {analysis['line_count']}"
        )
        logger.info("analyze_file_content function completed successfully")
        return json.dumps(analysis, indent=2)

    except Exception as e:
        logger.error(f"Error in analyze_file_content: {str(e)}")
        logger.info("analyze_file_content function completed with error")
        return json.dumps(
            {
                "error": f"Analysis failed: {str(e)}",
                "content_length": len(content) if content else 0,
            }
        )


def batch_retrieve_files(urls: str, include_metadata: bool = True) -> str:
    """
    Retrieve multiple files from a list of URLs.

    Args:
        urls (str): Comma-separated list of URLs
        include_metadata (bool): Whether to include metadata in responses

    Returns:
        str: JSON string with results for all URLs
    """
    try:
        url_list = [url.strip() for url in urls.split(",") if url.strip()]

        if not url_list:
            return json.dumps(
                {"success": False, "error": "No valid URLs provided"}
            )

        results = []
        total_start_time = time.time()

        for url in url_list:
            start_time = time.time()
            result = json.loads(retrieve_file_content(url, include_metadata))
            download_time = time.time() - start_time

            result["individual_download_time"] = round(download_time, 3)
            results.append(result)

        total_time = time.time() - total_start_time

        summary = {
            "total_urls": len(url_list),
            "successful_retrievals": len(
                [r for r in results if r.get("success", False)]
            ),
            "failed_retrievals": len(
                [r for r in results if not r.get("success", False)]
            ),
            "total_time": round(total_time, 3),
            "results": results,
        }

        return json.dumps(summary, indent=2)

    except Exception as e:
        return json.dumps(
            {"success": False, "error": f"Batch retrieval failed: {str(e)}"}
        )


def search_file_content(
    content: str, search_term: str, case_sensitive: bool = False
) -> str:
    """
    Search for specific terms within file content.

    Args:
        content (str): The file content to search
        search_term (str): The term to search for
        case_sensitive (bool): Whether the search should be case sensitive

    Returns:
        str: JSON string with search results
    """
    try:
        if not search_term:
            return json.dumps(
                {"success": False, "error": "Search term is required"}
            )

        lines = content.splitlines()
        matches = []

        for line_num, line in enumerate(lines, 1):
            if case_sensitive:
                if search_term in line:
                    matches.append(
                        {
                            "line_number": line_num,
                            "line_content": line.strip(),
                            "match_position": line.find(search_term),
                        }
                    )
            else:
                if search_term.lower() in line.lower():
                    matches.append(
                        {
                            "line_number": line_num,
                            "line_content": line.strip(),
                            "match_position": line.lower().find(
                                search_term.lower()
                            ),
                        }
                    )

        result = {
            "success": True,
            "search_term": search_term,
            "case_sensitive": case_sensitive,
            "total_matches": len(matches),
            "total_lines": len(lines),
            "matches": matches,
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps(
            {"success": False, "error": f"Search failed: {str(e)}"}
        )


# Create individual interfaces for each function
url_validation_demo = gr.Interface(
    fn=validate_url,
    inputs=gr.Textbox(
        placeholder="Enter URL to validate (e.g., https://example.com/file.txt)",
        label="URL",
        lines=2,
    ),
    outputs=gr.JSON(label="URL Validation Result"),
    title="URL Validation",
    description="Validate if a URL is accessible and extract file information.",
    examples=[
        ["https://raw.githubusercontent.com/gradio-app/gradio/main/README.md"],
        ["https://httpbin.org/json"],
        ["https://httpbin.org/xml"],
        ["https://raw.githubusercontent.com/python/cpython/main/README.md"],
    ],
)

file_retrieval_demo = gr.Interface(
    fn=retrieve_file_content,
    inputs=[
        gr.Textbox(
            placeholder="Enter URL of the file to retrieve",
            label="File URL",
            lines=2,
        ),
        gr.Checkbox(label="Include Metadata", value=True),
    ],
    outputs=gr.JSON(label="File Retrieval Result"),
    title="File Content Retrieval",
    description="Retrieve file content from HTTP servers with optional metadata.",
    examples=[
        [
            "https://raw.githubusercontent.com/gradio-app/gradio/main/README.md",
            True,
        ],
        ["https://httpbin.org/json", False],
        [
            "https://raw.githubusercontent.com/python/cpython/main/README.md",
            True,
        ],
    ],
)

content_analysis_demo = gr.Interface(
    fn=analyze_file_content,
    inputs=[
        gr.Textbox(
            placeholder="Enter file content to analyze",
            label="File Content",
            lines=10,
        ),
        gr.Dropdown(
            choices=[
                "auto",
                "text",
                "code",
                "json",
                "xml",
                "html",
                "python",
                "javascript",
                "java",
                "c",
            ],
            value="auto",
            label="File Type",
        ),
    ],
    outputs=gr.JSON(label="Content Analysis Result"),
    title="Content Analysis",
    description="Analyze file content for structure, metrics, and type detection.",
    examples=[
        [
            """def hello_world():
    print("Hello, World!")

class Example:
    def __init__(self):
        self.name = "example"
""",
            "auto",
        ],
        [
            """{
  "name": "example",
  "value": 42,
  "items": ["a", "b", "c"]
}""",
            "json",
        ],
    ],
)

content_search_demo = gr.Interface(
    fn=search_file_content,
    inputs=[
        gr.Textbox(
            placeholder="Enter file content to search",
            label="File Content",
            lines=10,
        ),
        gr.Textbox(
            placeholder="Enter search term", label="Search Term", lines=1
        ),
        gr.Checkbox(label="Case Sensitive", value=False),
    ],
    outputs=gr.JSON(label="Search Result"),
    title="Content Search",
    description="Search for specific terms within file content with line-by-line matching.",
    examples=[
        [
            """def function1():
    print("Hello")

def function2():
    print("World")
""",
            "def",
            False,
        ],
        [
            """import os
import sys
import json

def main():
    pass
""",
            "import",
            True,
        ],
    ],
)

batch_retrieval_demo = gr.Interface(
    fn=batch_retrieve_files,
    inputs=[
        gr.Textbox(
            placeholder="Enter URLs, one per line",
            label="URLs (one per line)",
            lines=5,
        ),
        gr.Checkbox(label="Include Metadata", value=True),
    ],
    outputs=gr.JSON(label="Batch Retrieval Result"),
    title="Batch File Retrieval",
    description="Retrieve multiple files from different URLs with summary statistics.",
    examples=[
        [
            """https://raw.githubusercontent.com/gradio-app/gradio/main/README.md
https://httpbin.org/json
https://raw.githubusercontent.com/python/cpython/main/README.md""",
            True,
        ]
    ],
)

# Create tabbed interface
demo = gr.TabbedInterface(
    [
        url_validation_demo,
        file_retrieval_demo,
        content_analysis_demo,
        content_search_demo,
        batch_retrieval_demo,
    ],
    [
        "URL Validation",
        "File Retrieval",
        "Content Analysis",
        "Content Search",
        "Batch Retrieval",
    ],
    title="HTTP File Retriever Server",
)

# Launch the interface and MCP server
if __name__ == "__main__":
    port = server_config["port"]
    logger.info(f"Starting {server_config['name']}")
    logger.info(f"Launching Gradio interface on port {port}")
    try:
        demo.launch(server_port=port, mcp_server=True)
        logger.info(f"{server_config['name']} started successfully")
    except Exception as e:
        logger.error(f"Failed to start {server_config['name']}: {str(e)}")
        raise
