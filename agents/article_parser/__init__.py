"""
Article Parser Agent V1.0
=========================
Life OS web article extraction and analysis.

Author: Claude AI Architect
Date: 2025-12-30
"""

from .article_parser_agent import (
    extract_article,
    article_parser_node,
    ArticleResult,
    ArticleSource,
    LifeOSDomain,
    is_article_url,
    extract_article_urls,
)

__version__ = "1.0.0"
__all__ = [
    "extract_article",
    "article_parser_node",
    "ArticleResult",
    "ArticleSource",
    "LifeOSDomain",
    "is_article_url",
    "extract_article_urls",
]
