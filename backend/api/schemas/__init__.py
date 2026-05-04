"""API 스키마 모듈"""
from .common import CrawlRequest, CrawlResponse
from .posts import PostResponse, StatsResponse
from .reports import DailyReportResponse, KeywordResponse, CharacterRankingResponse
from .characters import ChatServiceCharacterResponse, CrawlChatServicesRequest
from .news import NewsArticleResponse, CrawlNewsRequest
from .reviews import AppReviewResponse, AppReviewStatsResponse
from .bookmarks import BookmarkCreate, BookmarkUpdate, BookmarkResponse
from .samples import CharacterSampleRequest, CharacterSampleResponse

__all__ = [
    # Common
    'CrawlRequest', 'CrawlResponse',
    # Posts
    'PostResponse', 'StatsResponse',
    # Reports
    'DailyReportResponse', 'KeywordResponse', 'CharacterRankingResponse',
    # Characters
    'ChatServiceCharacterResponse', 'CrawlChatServicesRequest',
    # News
    'NewsArticleResponse', 'CrawlNewsRequest',
    # Reviews
    'AppReviewResponse', 'AppReviewStatsResponse',
    # Bookmarks
    'BookmarkCreate', 'BookmarkUpdate', 'BookmarkResponse',
    # Samples
    'CharacterSampleRequest', 'CharacterSampleResponse',
]
