import json
import logging
import os
import sys

# Add the project root to the path to import config_loader
sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
)

import gradio as gr  # noqa: E402
from textblob import TextBlob  # noqa: E402

from config_loader import get_config_loader  # noqa: E402
from logging_utils import (  # noqa: E402
    log_tool_call,
    log_tool_result,
    setup_logging,
)

# Set MCP logging to ERROR before any imports (will be overridden by config)
logging.getLogger("mcp").setLevel(logging.ERROR)
logging.getLogger("mcp.server").setLevel(logging.ERROR)
logging.getLogger("mcp.server.lowlevel.server").setLevel(logging.ERROR)

# Load configuration
config_loader = get_config_loader()
server_config = config_loader.get_server_config("basic_server")
logging_config = config_loader.get_logging_config()

# Setup logging with custom filters
logger = setup_logging(logging_config)


def sentiment_analysis(text: str) -> str:
    """
    Analyze the sentiment of the given text using natural language processing.

    This function performs sentiment analysis on text input using the TextBlob library.
    It evaluates the emotional tone and subjectivity of the text, providing both
    numerical scores and categorical assessments. The analysis is based on machine
    learning models trained on large text corpora.

    Args:
        text (str): The text to analyze for sentiment. Can be any length from a
                   single word to multiple paragraphs. The function works best with
                   complete sentences and natural language text.
                   Examples: "I love this product!", "This service is terrible",
                            "The weather is nice today"

    Returns:
        str: A JSON string containing the sentiment analysis results with the following structure:
        {
            "polarity": 0.8,           // Float between -1.0 (negative) and 1.0 (positive)
            "subjectivity": 0.6,       // Float between 0.0 (objective) and 1.0 (subjective)
            "assessment": "positive"   // String: "positive", "negative", or "neutral"
        }

        The polarity score indicates:
        - Positive values (0.1 to 1.0): Positive sentiment
        - Negative values (-1.0 to -0.1): Negative sentiment
        - Zero (0.0): Neutral sentiment

        The subjectivity score indicates:
        - High values (0.5 to 1.0): Subjective/opinionated text
        - Low values (0.0 to 0.5): Objective/factual text

    Raises:
        No exceptions are raised - all errors are returned in the JSON response.

    Examples:
        >>> result = sentiment_analysis("I absolutely love this amazing product!")
        >>> data = json.loads(result)
        >>> print(f"Polarity: {data['polarity']}")  # Likely around 0.8-1.0
        >>> print(f"Assessment: {data['assessment']}")  # "positive"

        >>> result = sentiment_analysis("This is terrible and I hate it.")
        >>> data = json.loads(result)
        >>> print(f"Polarity: {data['polarity']}")  # Likely around -0.8 to -1.0
        >>> print(f"Assessment: {data['assessment']}")  # "negative"

    Notes:
        - Uses TextBlob library for sentiment analysis
        - Polarity scores are rounded to 2 decimal places
        - Subjectivity scores are rounded to 2 decimal places
        - Assessment is automatically determined based on polarity threshold
        - Works with English text (TextBlob's primary language)
        - Performance may vary with very short text or non-English content
        - Results are logged for monitoring and debugging purposes
    """
    log_tool_call(logger, "sentiment_analysis", {"text_length": len(text)})

    try:
        blob = TextBlob(text)
        sentiment = blob.sentiment

        result = {
            "polarity": round(sentiment.polarity, 2),  # -1 (negative) to 1 (positive)
            "subjectivity": round(
                sentiment.subjectivity, 2
            ),  # 0 (objective) to 1 (subjective)
            "assessment": (
                "positive"
                if sentiment.polarity > 0
                else "negative" if sentiment.polarity < 0 else "neutral"
            ),
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
