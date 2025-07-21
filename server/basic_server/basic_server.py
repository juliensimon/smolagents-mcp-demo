import json
import logging
import os
import sys

import gradio as gr
from textblob import TextBlob

from config_loader import get_config_loader
from logging_utils import log_tool_call, log_tool_result, setup_logging

# Set MCP logging to ERROR before any imports (will be overridden by config)
logging.getLogger("mcp").setLevel(logging.ERROR)
logging.getLogger("mcp.server").setLevel(logging.ERROR)
logging.getLogger("mcp.server.lowlevel.server").setLevel(logging.ERROR)

# Add the project root to the path to import config_loader
sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ),
)

# Load configuration
config_loader = get_config_loader()
server_config = config_loader.get_server_config("basic_server")
logging_config = config_loader.get_logging_config()

# Setup logging with custom filters
logger = setup_logging(logging_config)


def sentiment_analysis(text: str) -> str:
    """
    Analyze the sentiment of the given text.

    Args:
        text (str): The text to analyze

    Returns:
        str: A JSON string containing polarity, subjectivity, and assessment
    """
    log_tool_call(logger, "sentiment_analysis", {"text_length": len(text)})

    try:
        blob = TextBlob(text)
        sentiment = blob.sentiment

        result = {
            "polarity": round(
                sentiment.polarity, 2
            ),  # -1 (negative) to 1 (positive)
            "subjectivity": round(
                sentiment.subjectivity, 2
            ),  # 0 (objective) to 1 (subjective)
            "assessment": "positive"
            if sentiment.polarity > 0
            else "negative"
            if sentiment.polarity < 0
            else "neutral",
        }

        log_tool_result(logger, "sentiment_analysis", result)
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error in sentiment_analysis: {str(e)}")
        return json.dumps({"error": f"Analysis failed: {str(e)}"})


# Create interface for sentiment analysis
demo = gr.Interface(
    fn=sentiment_analysis,
    inputs=gr.Textbox(
        placeholder="Enter text to analyze for sentiment...",
        label="Input Text",
        lines=5,
    ),
    outputs=gr.JSON(label="Sentiment Analysis Results"),
    title="Text Sentiment Analysis",
    description="Analyze the sentiment of text using TextBlob library",
    examples=[
        ["I love this product! It's absolutely amazing and works perfectly."],
        ["This is the worst experience I've ever had. Terrible service."],
        ["The weather is cloudy today with a chance of rain."],
        ["I'm feeling really excited about the new project we're starting!"],
        ["The movie was okay, nothing special but not bad either."],
    ],
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
