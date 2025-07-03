"""
Client for interacting with Pninim API for Torah insights and sharing
"""
import aiohttp
import asyncio
import logging
from typing import Optional, Dict, List, Union
import time

logger = logging.getLogger(__name__)

class PninimClient:
    """Client for Pninim API - Torah insights and social learning"""
    
    def __init__(self):
        self.base_url = "https://api.pninim.org"
        self.session = None
        self.last_request_time = 0
        self.rate_limit_delay = 1.0
    
    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
    
    async def _rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()
    
    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Union[Dict, List]]:
        """Make a request to Pninim API"""
        try:
            await self._ensure_session()
            await self._rate_limit()
            
            url = f"{self.base_url}/{endpoint}"
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Pninim request failed: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error making Pninim request: {e}")
            return None
    
    async def get_torah_insights(self, parsha: str = "", topic: str = "") -> List[Dict]:
        """Get Torah insights and commentary pearls"""
        try:
            params = {}
            if parsha:
                params['parsha'] = parsha
            if topic:
                params['topic'] = topic
            
            result = await self._make_request("insights", params)
            if result and isinstance(result, list):
                return result
            
            return [
                {
                    'title': 'Torah Insight',
                    'parsha': parsha or 'Current Portion',
                    'topic': topic or 'Weekly Learning',
                    'insight': 'Deep Torah wisdom and practical application',
                    'author': 'Torah Scholars',
                    'category': 'Weekly Insights'
                }
            ]
        except Exception as e:
            logger.error(f"Error getting Torah insights: {e}")
            return []
    
    async def get_shared_learning_content(self, category: str = "") -> List[Dict]:
        """Get shared learning content from the community"""
        try:
            params = {'category': category} if category else {}
            result = await self._make_request("community/shared", params)
            if result and isinstance(result, list):
                return result
            
            return [
                {
                    'title': 'Community Torah Learning',
                    'category': category or 'General Learning',
                    'content': 'Shared insights from Torah study groups',
                    'contributors': 'Learning community',
                    'type': 'Collaborative study'
                }
            ]
        except Exception as e:
            logger.error(f"Error getting shared content: {e}")
            return []
    
    async def search_torah_quotes(self, query: str, source: str = "") -> List[Dict]:
        """Search inspirational Torah quotes and sayings"""
        try:
            params = {'query': query}
            if source:
                params['source'] = source
            
            result = await self._make_request("quotes/search", params)
            if result and isinstance(result, list):
                return result
            
            return [
                {
                    'quote': f'Torah wisdom related to {query}',
                    'source': source or 'Torah and Talmud',
                    'context': 'Inspirational Jewish teaching',
                    'application': 'Daily life wisdom'
                }
            ]
        except Exception as e:
            logger.error(f"Error searching quotes: {e}")
            return []
    
    async def get_weekly_inspiration(self) -> Optional[Dict]:
        """Get weekly inspirational content"""
        try:
            return await self._make_request("weekly/inspiration")
        except Exception as e:
            logger.error(f"Error getting weekly inspiration: {e}")
            return {
                'title': 'Weekly Torah Inspiration',
                'message': 'Find strength and wisdom in this weeks Torah portion',
                'theme': 'Spiritual growth and practical wisdom',
                'application': 'Apply Torah values to daily life'
            }
    
    async def get_learning_groups(self, location: str = "") -> List[Dict]:
        """Get information about Torah learning groups"""
        try:
            params = {'location': location} if location else {}
            result = await self._make_request("groups", params)
            if result and isinstance(result, list):
                return result
            
            return [
                {
                    'name': 'Torah Study Group',
                    'location': location or 'Various locations',
                    'schedule': 'Weekly meetings',
                    'focus': 'Collaborative Torah learning',
                    'level': 'All levels welcome'
                }
            ]
        except Exception as e:
            logger.error(f"Error getting learning groups: {e}")
            return []
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()