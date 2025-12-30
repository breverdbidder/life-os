"""
Article Parser Agent for Life OS

Parses web articles (including JS-rendered) and classifies by Life OS domains.
Uses Jina AI Reader (FREE) for content extraction.
"""

from .article_parser_node import (
    ArticleParserNode,
    article_parser_node,
    LIFE_OS_DOMAINS
)

__all__ = [
    'ArticleParserNode',
    'article_parser_node',
    'LIFE_OS_DOMAINS'
]

__version__ = '1.0.0'
