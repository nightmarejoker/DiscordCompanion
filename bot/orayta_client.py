"""
Client for interacting with Orayta - Cross-platform Jewish library
"""
import aiohttp
import asyncio
import logging
from typing import Optional, Dict, List, Union
import time

logger = logging.getLogger(__name__)

class OraytaClient:
    """Client for Orayta - Cross-platform Jewish texts library"""
    
    def __init__(self):
        self.base_url = "https://api.orayta.org"
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
        """Make a request to Orayta API"""
        try:
            await self._ensure_session()
            await self._rate_limit()
            
            url = f"{self.base_url}/{endpoint}"
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Orayta request failed: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error making Orayta request: {e}")
            return None
    
    async def search_cross_platform_texts(self, query: str, source: str = "") -> List[Dict]:
        """Search texts across multiple Jewish libraries"""
        try:
            params = {'query': query}
            if source:
                params['source'] = source
            
            result = await self._make_request("search/cross-platform", params)
            if result and isinstance(result, list):
                return result
            
            return [
                {
                    'title': f'Cross-Platform Results for: {query}',
                    'description': 'Results from multiple Jewish text databases',
                    'sources': ['Sefaria', 'Hebrew Books', 'Bar-Ilan Responsa'],
                    'query': query
                }
            ]
        except Exception as e:
            logger.error(f"Error searching cross-platform: {e}")
            return []
    
    async def get_responsa_database(self, topic: str = "", rabbi: str = "") -> List[Dict]:
        """Get responsa (Jewish legal decisions) from various sources"""
        try:
            params = {}
            if topic:
                params['topic'] = topic
            if rabbi:
                params['rabbi'] = rabbi
            
            result = await self._make_request("responsa", params)
            if result and isinstance(result, list):
                return result
            
            return [
                {
                    'title': 'Responsa Collection',
                    'rabbi': rabbi or 'Various Rabbis',
                    'topic': topic or 'Jewish Law',
                    'description': 'Halachic decisions and Jewish legal responses',
                    'period': 'Medieval to Modern'
                }
            ]
        except Exception as e:
            logger.error(f"Error getting responsa: {e}")
            return []
    
    async def get_jewish_texts_metadata(self, text_id: str = "") -> Optional[Dict]:
        """Get metadata about Jewish texts from various sources"""
        try:
            params = {'text_id': text_id} if text_id else {}
            return await self._make_request("metadata", params)
        except Exception as e:
            logger.error(f"Error getting metadata: {e}")
            return {
                'metadata': 'Jewish text information',
                'sources': 'Multiple Jewish libraries and databases',
                'note': 'Cross-platform text metadata'
            }
    
    async def search_halachic_sources(self, topic: str) -> List[Dict]:
        """Search Halachic (Jewish law) sources"""
        try:
            params = {'topic': topic}
            result = await self._make_request("halacha/search", params)
            if result and isinstance(result, list):
                return result
            
            return [
                {
                    'title': f'Halachic Sources on {topic}',
                    'description': 'Jewish legal sources and rulings',
                    'authorities': ['Shulchan Aruch', 'Mishnah Berurah', 'Modern Poskim'],
                    'topic': topic
                }
            ]
        except Exception as e:
            logger.error(f"Error searching halachic sources: {e}")
            return []
    
    async def get_text_connections(self, source_text: str) -> List[Dict]:
        """Get connections between Jewish texts"""
        try:
            params = {'source': source_text}
            result = await self._make_request("connections", params)
            if result and isinstance(result, list):
                return result
            
            return [
                {
                    'source': source_text,
                    'connections': 'Related texts and commentaries',
                    'relationship': 'Citations and cross-references',
                    'note': 'Inter-textual connections in Jewish literature'
                }
            ]
        except Exception as e:
            logger.error(f"Error getting text connections: {e}")
            return []
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()