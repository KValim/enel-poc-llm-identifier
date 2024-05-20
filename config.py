"""
This module defines the configuration settings for the Flask application.

It includes settings for secret keys, API keys, allowed file extensions, and the model used for OpenAI.
"""

import os

class Config:
    """
    Configuration settings for the Flask application.

    Attributes:
        SECRET_KEY (str): The secret key for the application, used for session management and other security purposes.
        OPENAI_API_KEY (str): The API key for accessing OpenAI services.
        ALLOWED_EXTENSIONS (set): A set of allowed file extensions for file uploads.
        MODEL (str): The model identifier used for OpenAI API requests.
    """
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'supersecretkey'
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MODEL = "gpt-4o"
