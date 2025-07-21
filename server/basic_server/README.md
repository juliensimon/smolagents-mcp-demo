# Basic Server - Text Sentiment Analysis

A simple MCP server implementation for text sentiment analysis using TextBlob library. This server provides basic sentiment analysis capabilities with a clean, easy-to-use interface.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Required packages: `gradio`, `textblob`

### Installation
```bash
# Install required packages
pip install gradio textblob

# Navigate to the basic server directory
cd server/basic_server
```

### Launch Server
```bash
python basic_server.py
```
**Server Port:** 7860
**Access:** http://localhost:7860



## 📋 Features

### Server Functionality
- **Sentiment Analysis**: Analyze text for emotional tone and subjectivity
- **Polarity Scoring**: -1 (negative) to +1 (positive) sentiment scale
- **Subjectivity Analysis**: 0 (objective) to 1 (subjective) content assessment
- **JSON Response Format**: Structured output for easy integration



## 🎯 Usage Examples

### Basic Sentiment Analysis
```python
# Example text for analysis
text = "I absolutely love this new feature! It's exactly what I needed."

# Expected result:
{
  "polarity": 0.8,
  "subjectivity": 0.6,
  "assessment": "positive"
}
```

### Negative Sentiment
```python
text = "This is the worst experience I've ever had. Terrible service."

# Expected result:
{
  "polarity": -0.8,
  "subjectivity": 0.7,
  "assessment": "negative"
}
```

### Neutral Content
```python
text = "The weather is cloudy today with a chance of rain."

# Expected result:
{
  "polarity": 0.0,
  "subjectivity": 0.1,
  "assessment": "neutral"
}
```

## 🔧 Configuration

### Server Configuration
The server uses a simple configuration with TextBlob for sentiment analysis:

```python
# Server configuration
demo = gr.Interface(
    fn=sentiment_analysis,
    inputs=gr.Textbox(placeholder="Enter text to analyze..."),
    outputs=gr.Textbox(),
    title="Text Sentiment Analysis",
    description="Analyze the sentiment of text using TextBlob"
)
```



## 🌐 Interface Features

### Server Interface
- **Simple Text Input**: Large text area for input
- **JSON Output**: Structured sentiment analysis results
- **Real-time Processing**: Instant analysis feedback
- **Error Handling**: Graceful error management



## 📊 API Reference

### Sentiment Analysis Function
```python
def sentiment_analysis(text: str) -> str:
    """
    Analyze the sentiment of the given text.

    Args:
        text (str): The text to analyze

    Returns:
        str: JSON string containing polarity, subjectivity, and assessment
    """
```

### Response Format
```json
{
  "polarity": 0.8,           // -1.0 to 1.0 (negative to positive)
  "subjectivity": 0.6,       // 0.0 to 1.0 (objective to subjective)
  "assessment": "positive"   // "positive", "negative", or "neutral"
}
```

## 🔍 Logging

The server includes comprehensive logging for monitoring and debugging:

### Log File
- **Location**: `basic_server.log`
- **Format**: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- **Level**: INFO

### Log Entries
```
2025-07-21 14:22:05,840 - basic_server - INFO - Starting sentiment_analysis function
2025-07-21 14:22:05,840 - basic_server - INFO - Input text length: 25 characters
2025-07-21 14:22:05,841 - basic_server - INFO - Sentiment analysis completed - Polarity: 0.8, Subjectivity: 0.6, Assessment: positive
2025-07-21 14:22:05,841 - basic_server - INFO - sentiment_analysis function completed successfully
```

## 🚨 Troubleshooting

### Common Issues

**1. Port Already in Use**
```bash
# Check if port is in use
lsof -i :7860

# Kill process using the port
kill -9 <PID>
```

**2. Missing Dependencies**
```bash
# Install missing packages
pip install gradio textblob
```

**3. Import Errors**
```bash
# Verify Python environment
python -c "import gradio, textblob; print('Dependencies OK')"
```

### Error Messages

**"Failed to create interface"**
- Check if all required packages are installed
- Verify configuration file format
- Ensure server is running

**"Connection refused"**
- Verify server is started on correct port
- Check firewall settings
- Ensure no other process is using the port

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
client = MCPClient({"url": "http://127.0.0.1:7860/gradio_api/mcp/sse"})

# Get available tools
tools = client.get_tools()

# Use sentiment analysis
result = client.call_tool("sentiment_analysis", {"text": "I love this!"})
```

## 📈 Performance

### Processing Speed
- **Small texts (< 100 chars)**: ~10-50ms
- **Medium texts (100-1000 chars)**: ~50-200ms
- **Large texts (> 1000 chars)**: ~200-500ms

### Memory Usage
- **Minimal memory footprint**: ~10-50MB
- **Efficient text processing**: Stream-based analysis
- **No persistent storage**: Stateless operation

## 🔒 Security

### Input Validation
- All text inputs are validated
- Maximum text length limits
- Safe text processing

### Local Processing
- No external API calls for sentiment analysis
- Local TextBlob processing
- No data transmission to external services

## 🤝 Contributing

### Development Setup
1. Clone the repository
2. Install dependencies: `pip install gradio textblob`
3. Run tests: `python -m pytest tests/`
4. Start development server: `python basic_server.py`

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings for all functions
- Include error handling

### Testing
- Test with various text types
- Verify error handling
- Check edge cases
- Validate output formats

## 📚 Additional Resources

### Documentation
- [TextBlob Documentation](https://textblob.readthedocs.io/)
- [Gradio Documentation](https://gradio.app/docs/)
- [MCP Protocol](https://modelcontextprotocol.io/)

### Related Projects
- [TextBlob](https://textblob.readthedocs.io/)
- [Gradio](https://gradio.app/)
- [Natural Language Toolkit](https://www.nltk.org/)

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review error messages carefully
3. Verify configuration settings
4. Test with simple examples first
5. Check server logs for detailed information

---

**Note:** This server is designed for development and testing purposes. For production use, ensure proper security measures and error handling are implemented.
