"""
Configuration management utilities.
"""

import os
from typing import Optional
from pydantic import BaseModel


class Settings(BaseModel):
    """Application settings."""
    
    # Application
    app_name: str = "Product Catalog API"
    app_version: str = "3.0.0"
    debug: bool = False
    
    # Matcher
    use_enhanced_matcher: bool = True
    fuzzy_threshold: float = 0.70
    default_search_limit: int = 10
    default_fuzzy_limit: int = 30
    
    # Data
    data_file_path: str = "data/product_match_dictionary.json"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_prefix = ""  # No prefix for environment variables


def get_settings() -> Settings:
    """
    Get application settings from environment variables.
    
    Environment variables override default values:
    - USE_ENHANCED_MATCHER: Enable/disable enhanced matcher
    - LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR)
    - DEFAULT_SEARCH_LIMIT: Default number of search results
    - etc.
    
    Returns:
        Settings instance
    
    Example:
        >>> from src.utils import get_settings
        >>> settings = get_settings()
        >>> print(settings.app_name)
        'Product Catalog API'
    """
    return Settings(
        use_enhanced_matcher=os.getenv("USE_ENHANCED_MATCHER", "true").lower() == "true",
        fuzzy_threshold=float(os.getenv("DEFAULT_FUZZY_THRESHOLD", "0.70")),
        default_search_limit=int(os.getenv("DEFAULT_SEARCH_LIMIT", "10")),
        default_fuzzy_limit=int(os.getenv("DEFAULT_FUZZY_LIMIT", "30")),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        debug=os.getenv("DEBUG", "false").lower() == "true",
    )


# Made with Bob