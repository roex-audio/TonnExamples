"""
Configuration module for Tonn API examples.

This module handles API key loading and base URL configuration.
"""

import os
import sys

# Load .env file if present (same behavior as Node.js dotenv)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, that's fine

# Base URL for the Tonn API
BASE_URL = "https://tonn.roexaudio.com"


def get_api_key() -> str:
    """
    Get the Tonn API key from environment variables.
    
    The API key should be set in the TONN_API_KEY environment variable.
    You can get an API key from: https://tonn-portal.roexaudio.com
    
    Returns:
        str: The API key
        
    Raises:
        SystemExit: If the API key is not set
    """
    api_key = os.environ.get("TONN_API_KEY")
    
    if not api_key:
        print("=" * 60)
        print("ERROR: TONN_API_KEY environment variable not set")
        print("=" * 60)
        print()
        print("To fix this:")
        print("  1. Get an API key from: https://tonn-portal.roexaudio.com")
        print("  2. Set the environment variable:")
        print()
        print("     On macOS/Linux:")
        print("       export TONN_API_KEY=your_api_key_here")
        print()
        print("     On Windows (Command Prompt):")
        print("       set TONN_API_KEY=your_api_key_here")
        print()
        print("     On Windows (PowerShell):")
        print("       $env:TONN_API_KEY=\"your_api_key_here\"")
        print()
        print("  3. Or create a .env file with:")
        print("       TONN_API_KEY=your_api_key_here")
        print()
        sys.exit(1)
    
    return api_key


def get_headers(api_key: str = None) -> dict:
    """
    Get the standard headers for Tonn API requests.
    
    Args:
        api_key: Optional API key. If not provided, will be loaded from environment.
        
    Returns:
        dict: Headers dictionary for API requests
    """
    if api_key is None:
        api_key = get_api_key()
        
    return {
        "Content-Type": "application/json",
        "x-api-key": api_key
    }

