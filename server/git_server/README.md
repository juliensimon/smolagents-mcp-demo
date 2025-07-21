# Git Server - Version Control Operations

A comprehensive MCP server implementation for Git operations and version control management. This server provides file-specific Git operations including status checking, staging, committing, diff viewing, and log retrieval.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Required packages: `gradio`, `subprocess`
- Git repository (for git operations)

### Installation
```bash
# Install required packages
pip install gradio

# Navigate to the git server directory
cd server/git_server

# Ensure you're in a git repository
git init  # if not already initialized
```

### Launch Server
```bash
python git_server.py
```
**Server Port:** 7867
**Access:** http://localhost:7867

## 📋 Features

### Server Functionality
The server provides 5 comprehensive Git operations:

1. **Git Status**
   - Check file tracking status
   - Identify modified, staged, or untracked files
   - Get last commit information
   - Comprehensive status reporting

2. **Git Add**
   - Stage files for commit
   - Add files to Git tracking
   - Update staging area
   - Status verification after staging

3. **Git Commit**
   - Commit staged changes
   - Custom commit messages
   - Commit hash generation
   - Pre-commit validation

4. **Git Diff**
   - View file changes
   - Staged vs unstaged changes
   - Line-by-line difference analysis
   - Change statistics

5. **Git Log**
   - View commit history
   - File-specific commit tracking
   - Commit metadata (author, date, message)
   - Configurable log limits



## 🎯 Usage Examples

### Git Status Check
```python
# Check status of a file
file_path = "server/git_server/git_server.py"

# Expected result:
{
  "file_path": "server/git_server/git_server.py",
  "relative_path": "server/git_server/git_server.py",
  "status": "modified",
  "message": "File has been modified",
  "last_commit": {
    "hash": "a1b2c3d4",
    "author": "John Doe",
    "date": "2025-07-21",
    "message": "Update test client"
  }
}
```

### Git Add Operation
```python
# Stage a file for commit
file_path = "new_file.py"

# Expected result:
{
  "file_path": "new_file.py",
  "relative_path": "new_file.py",
  "action": "added",
  "success": true,
  "message": "File new_file.py has been added to staging",
  "current_status": "A "
}
```

### Git Commit Operation
```python
# Commit staged changes
file_path = "modified_file.py"
commit_message = "Fix bug in data processing"

# Expected result:
{
  "file_path": "modified_file.py",
  "relative_path": "modified_file.py",
  "action": "committed",
  "success": true,
  "message": "Changes committed successfully",
  "commit_hash": "e5f6g7h8",
  "commit_message": "Fix bug in data processing"
}
```

### Git Diff Viewing
```python
# View changes in a file
file_path = "server/git_server/git_server.py"
staged = false

# Expected result:
{
  "file_path": "server/git_server/git_server.py",
  "relative_path": "server/git_server/git_server.py",
  "staged": false,
  "diff": "@@ -10,7 +10,7 @@\n def git_status(file_path: str) -> str:\n     logger.info(f\"Input file_path: {file_path}\")\n     \n     try:\n-        # Check if file exists\n+        # Validate file existence\n         if not os.path.exists(file_path):\n             return json.dumps({\"error\": f\"File {file_path} does not exist\"})\n",
  "lines_added": 1,
  "lines_removed": 1,
  "has_changes": true
}
```

### Git Log Retrieval
```python
# Get commit history for a file
file_path = "README.md"
limit = 5

# Expected result:
{
  "file_path": "README.md",
  "relative_path": "README.md",
  "limit": 5,
  "commits": [
    {
      "hash": "a1b2c3d4",
      "author": "John Doe",
      "date": "2025-07-21",
      "message": "Update documentation"
    },
    {
      "hash": "e5f6g7h8",
      "author": "Jane Smith",
      "date": "2025-07-20",
      "message": "Initial commit"
    }
  ],
  "total_commits": 2
}
```

## 🔧 Configuration

### Server Configuration
The server uses comprehensive logging and Git integration:

```python
# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('git_server.log'),
        logging.StreamHandler()
    ]
)
```



## 🌐 Interface Features

### Server Interface
- **Multi-function Support**: 5 different Git operations
- **JSON Output**: Structured Git operation results
- **Error Handling**: Comprehensive error management
- **Logging**: Detailed operation logging



### Interactive Elements
- **File Path Input**: Text inputs for file paths
- **Commit Message Input**: Text areas for commit messages
- **Checkboxes**: Toggle staged/unstaged diff viewing
- **JSON Outputs**: Structured results display
- **Examples**: Pre-filled examples for quick testing

## 📊 API Reference

### Core Git Functions

#### 1. Git Status
```python
def git_status(file_path: str) -> str:
    """
    Get the git status of a specific file.

    Args:
        file_path (str): Path to the file to check git status

    Returns:
        str: JSON string with git status information
    """
```

#### 2. Git Add
```python
def git_add(file_path: str) -> str:
    """
    Add a file to git staging area.

    Args:
        file_path (str): Path to the file to add

    Returns:
        str: JSON string with add operation result
    """
```

#### 3. Git Commit
```python
def git_commit(file_path: str, commit_message: str) -> str:
    """
    Commit changes for a specific file.

    Args:
        file_path (str): Path to the file to commit
        commit_message (str): Commit message

    Returns:
        str: JSON string with commit operation result
    """
```

#### 4. Git Diff
```python
def git_diff(file_path: str, staged: bool = False) -> str:
    """
    Get git diff for a specific file.

    Args:
        file_path (str): Path to the file to get diff for
        staged (bool): Whether to show staged changes

    Returns:
        str: JSON string with diff information
    """
```

#### 5. Git Log
```python
def git_log(file_path: str, limit: int = 5) -> str:
    """
    Get git log for a specific file.

    Args:
        file_path (str): Path to the file to get log for
        limit (int): Maximum number of commits to show

    Returns:
        str: JSON string with log information
    """
```

### Response Formats

#### Status Response
```json
{
  "file_path": "example.py",
  "relative_path": "example.py",
  "status": "modified",
  "message": "File has been modified",
  "last_commit": {
    "hash": "a1b2c3d4",
    "author": "John Doe",
    "date": "2025-07-21",
    "message": "Update example"
  }
}
```

#### Add Response
```json
{
  "file_path": "new_file.py",
  "relative_path": "new_file.py",
  "action": "added",
  "success": true,
  "message": "File new_file.py has been added to staging"
}
```

#### Commit Response
```json
{
  "file_path": "modified_file.py",
  "relative_path": "modified_file.py",
  "action": "committed",
  "success": true,
  "message": "Changes committed successfully",
  "commit_hash": "e5f6g7h8",
  "commit_message": "Fix bug"
}
```

## 🔍 Logging

The server includes comprehensive logging for monitoring and debugging:

### Log File
- **Location**: `git_server.log`
- **Format**: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- **Level**: INFO

### Log Entries
```
2025-07-21 14:22:05,840 - git_server - INFO - Starting git_status function
2025-07-21 14:22:05,840 - git_server - INFO - Input file_path: example.py
2025-07-21 14:22:05,841 - git_server - INFO - Git status completed - Status: modified, Message: File has been modified
2025-07-21 14:22:05,841 - git_server - INFO - git_status function completed successfully
```

## 🚨 Troubleshooting

### Common Issues

**1. Port Already in Use**
```bash
# Check if port is in use
lsof -i :7867

# Kill process using the port
kill -9 <PID>
```

**2. Git Repository Not Found**
```bash
# Ensure you're in a git repository
git init
git add .
git commit -m "Initial commit"
```

**3. File Not Found**
```bash
# Check if file exists
ls -la your_file.py

# Use absolute path if needed
python git_server.py
```

### Error Messages

**"Directory is not a git repository"**
- Run `git init` to initialize repository
- Ensure you're in the correct directory
- Check git configuration

**"File does not exist"**
- Verify file path is correct
- Use absolute paths if needed
- Check file permissions

**"Failed to get git status"**
- Check git installation
- Verify git configuration
- Ensure file is in repository

## 🔄 Integration

### MCP Protocol Support
The server implements the Model Context Protocol for AI-powered interactions:

- **Tool Registration**: Automatic tool discovery
- **JSON Communication**: Structured data exchange
- **Error Handling**: Robust error management
- **Logging**: Comprehensive operation logging

### Client Integration
```python
# Example client usage
from smolagents import MCPClient

# Connect to server
client = MCPClient({"url": "http://127.0.0.1:7867/gradio_api/mcp/sse"})

# Get available tools
tools = client.get_tools()

# Use git status
result = client.call_tool("git_status", {"file_path": "example.py"})
```

## 📈 Performance

### Processing Speed
- **Status check**: ~50-200ms
- **Add operation**: ~100-300ms
- **Commit operation**: ~200-500ms
- **Diff viewing**: ~100-1000ms (depends on file size)
- **Log retrieval**: ~100-500ms

### Memory Usage
- **Efficient subprocess calls**: Minimal memory overhead
- **Stream-based processing**: Memory-efficient operations
- **No persistent storage**: Stateless operation

## 🔒 Security

### Input Validation
- All file paths are validated
- Path traversal protection
- Safe subprocess execution

### Local Operations
- All Git operations are local
- No external API calls
- No data transmission to external services

## 🤝 Contributing

### Development Setup
1. Clone the repository
2. Install dependencies: `pip install gradio`
3. Initialize git repository: `git init`
4. Start development server: `python git_server.py`

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings for all functions
- Include error handling

### Testing
- Test with various file types
- Verify error handling
- Check edge cases
- Validate output formats

## 📚 Additional Resources

### Documentation
- [Git Documentation](https://git-scm.com/doc)
- [Gradio Documentation](https://gradio.app/docs/)
- [MCP Protocol](https://modelcontextprotocol.io/)

### Related Projects
- [GitPython](https://gitpython.readthedocs.io/)
- [PyGit2](https://www.pygit2.org/)
- [Git](https://git-scm.com/)

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review error messages carefully
3. Verify git repository setup
4. Test with simple examples first
5. Check server logs for detailed information

---

**Note:** This server is designed for development and testing purposes. For production use, ensure proper security measures and error handling are implemented.
