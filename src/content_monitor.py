"""
Content monitoring from multiple streams (RSS, News API, Reddit)
"""
import feedparser
import requests
import asyncio
import aiohttp
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from src.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentItem:
    """Represents a piece of content from any source"""
    def __init__(self, title: str, text: str, url: str, source: str, published_at: Optional[datetime] = None):
        self.title = title
        self.text = text
        self.url = url
        self.source = source
        self.published_at = published_at or datetime.utcnow()


class RSSMonitor:
    """Monitor RSS feeds from major news outlets"""
    
    RSS_FEEDS = [
        ("BBC News", "http://feeds.bbci.co.uk/news/rss.xml"),
        ("Reuters", "https://www.reutersagency.com/feed/"),
        ("AP News", "https://apnews.com/index.rss"),
        ("CNN", "http://rss.cnn.com/rss/cnn_topstories.rss"),
        ("Al Jazeera", "https://www.aljazeera.com/xml/rss/all.xml"),
    ]
    
    async def fetch_feed(self, name: str, url: str) -> List[ContentItem]:
        """Fetch and parse a single RSS feed"""
        try:
            feed = feedparser.parse(url)
            items = []
            
            for entry in feed.entries[:10]:  # Limit to recent 10 items
                title = entry.get('title', '')
                summary = entry.get('summary', '') or entry.get('description', '')
                link = entry.get('link', '')
                
                # Parse published date
                published = None
                if hasattr(entry, 'published_parsed'):
                    published = datetime(*entry.published_parsed[:6])
                
                # Filter for crisis-related content
                if self._is_crisis_related(title + " " + summary):
                    items.append(ContentItem(
                        title=title,
                        text=summary,
                        url=link,
                        source=name,
                        published_at=published
                    ))
            
            logger.info(f"Fetched {len(items)} crisis-related items from {name}")
            return items
            
        except Exception as e:
            logger.error(f"Error fetching RSS feed {name}: {e}")
            return []
    
    def _is_crisis_related(self, text: str) -> bool:
        """Check if content is related to a crisis"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in settings.crisis_keywords)
    
    async def fetch_all(self) -> List[ContentItem]:
        """Fetch all RSS feeds concurrently"""
        tasks = [self.fetch_feed(name, url) for name, url in self.RSS_FEEDS]
        results = await asyncio.gather(*tasks)
        
        # Flatten results
        all_items = []
        for items in results:
            all_items.extend(items)
        
        return all_items


class NewsAPIMonitor:
    """Monitor news using NewsAPI"""
    
    def __init__(self):
        self.api_key = settings.news_api_key
        self.base_url = "https://newsapi.org/v2/everything"
    
    async def fetch_news(self) -> List[ContentItem]:
        """Fetch crisis-related news from NewsAPI"""
        if not self.api_key:
            logger.warning("NewsAPI key not configured, skipping")
            return []
        
        try:
            # Build query from crisis keywords
            query = " OR ".join(settings.crisis_keywords[:5])  # Limit query length
            
            params = {
                'q': query,
                'apiKey': self.api_key,
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': 20,
                'from': (datetime.utcnow() - timedelta(hours=24)).isoformat()
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        items = []
                        
                        for article in data.get('articles', []):
                            items.append(ContentItem(
                                title=article.get('title', ''),
                                text=article.get('description', '') or article.get('content', ''),
                                url=article.get('url', ''),
                                source=article.get('source', {}).get('name', 'NewsAPI'),
                                published_at=datetime.fromisoformat(article.get('publishedAt', '').replace('Z', '+00:00'))
                            ))
                        
                        logger.info(f"Fetched {len(items)} articles from NewsAPI")
                        return items
                    else:
                        logger.error(f"NewsAPI error: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error fetching from NewsAPI: {e}")
            return []


class RedditMonitor:
    """Monitor Reddit for crisis-related discussions"""
    
    SUBREDDITS = [
        'worldnews',
        'news',
        'Coronavirus',
        'climate',
        'geopolitics'
    ]
    
    async def fetch_reddit(self) -> List[ContentItem]:
        """Fetch top posts from crisis-related subreddits"""
        try:
            items = []
            
            async with aiohttp.ClientSession() as session:
                for subreddit in self.SUBREDDITS:
                    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=10"
                    headers = {'User-Agent': settings.reddit_user_agent}
                    
                    async with session.get(url, headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            for post in data.get('data', {}).get('children', []):
                                post_data = post.get('data', {})
                                title = post_data.get('title', '')
                                selftext = post_data.get('selftext', '')
                                
                                if self._is_crisis_related(title + " " + selftext):
                                    items.append(ContentItem(
                                        title=title,
                                        text=selftext or title,
                                        url=f"https://reddit.com{post_data.get('permalink', '')}",
                                        source=f"r/{subreddit}",
                                        published_at=datetime.fromtimestamp(post_data.get('created_utc', 0))
                                    ))
            
            logger.info(f"Fetched {len(items)} crisis-related posts from Reddit")
            return items
            
        except Exception as e:
            logger.error(f"Error fetching from Reddit: {e}")
            return []
    
    def _is_crisis_related(self, text: str) -> bool:
        """Check if content is related to a crisis"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in settings.crisis_keywords)


class ContentAggregator:
    """Aggregate content from all sources"""
    
    def __init__(self):
        self.rss_monitor = RSSMonitor()
        self.news_monitor = NewsAPIMonitor()
        self.reddit_monitor = RedditMonitor()
    
    async def fetch_all_content(self) -> List[ContentItem]:
        """Fetch content from all sources concurrently"""
        logger.info("Starting content aggregation...")
        
        tasks = [
            self.rss_monitor.fetch_all(),
            self.news_monitor.fetch_news(),
            self.reddit_monitor.fetch_reddit()
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Flatten and deduplicate
        all_items = []
        seen_urls = set()
        
        for items in results:
            for item in items:
                if item.url not in seen_urls:
                    all_items.append(item)
                    seen_urls.add(item.url)
        
        logger.info(f"Total unique content items: {len(all_items)}")
        return all_items
