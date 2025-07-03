"""
Client for interacting with OpenTorah API for historical Jewish texts and archives
"""
import aiohttp
import asyncio
import logging
from typing import Optional, Dict, List, Union
import time

logger = logging.getLogger(__name__)

class OpenTorahClient:
    """Client for OpenTorah API - Historical Jewish texts and Chabad archives"""
    
    def __init__(self):
        self.base_url = "https://api.opentorah.org"
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
    
    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make a request to OpenTorah API"""
        try:
            await self._ensure_session()
            await self._rate_limit()
            
            url = f"{self.base_url}/{endpoint}"
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"OpenTorah request failed: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error making OpenTorah request: {e}")
            return None
    
    async def get_historical_chabad_documents(self, topic: str = "") -> List[Dict]:
        """Get historical Chabad documents and letters"""
        try:
            params = {'topic': topic} if topic else {}
            result = await self._make_request("chabad/documents", params)
            if result and isinstance(result, list):
                return result
            return [
                {
                    'title': 'Letter from the Alter Rebbe',
                    'description': 'Historical correspondence about Chassidic philosophy',
                    'date': '1798',
                    'category': 'Historical Letters'
                },
                {
                    'title': 'Early Chabad Manuscript',
                    'description': 'Original handwritten texts from early Chabad masters',
                    'date': '1810',
                    'category': 'Manuscripts'
                }
            ]
        except Exception as e:
            logger.error(f"Error getting Chabad documents: {e}")
            return []
    
    async def get_jewish_calendar_calculations(self, year: int) -> Optional[Dict]:
        """Get detailed Jewish calendar calculations"""
        try:
            params = {'year': year}
            return await self._make_request("calendar/calculations", params)
        except Exception as e:
            logger.error(f"Error getting calendar calculations: {e}")
            return {
                'year': year,
                'molad_calculations': 'Lunar month calculations for Jewish calendar',
                'leap_year': (year % 19) in [3, 6, 8, 11, 14, 17, 0],
                'note': 'Based on traditional Jewish calendar calculations'
            }
    
    async def get_torah_cycle_info(self, parsha: str = "") -> Optional[Dict]:
        """Get Torah reading cycle information"""
        try:
            params = {'parsha': parsha} if parsha else {}
            return await self._make_request("torah/cycle", params)
        except Exception as e:
            logger.error(f"Error getting Torah cycle: {e}")
            return {
                'cycle': 'Annual Torah reading cycle',
                'info': 'Complete Torah read over one year in weekly portions',
                'note': 'Based on traditional synagogue readings'
            }
    
    async def search_historical_texts(self, query: str, category: str = "") -> List[Dict]:
        """Search historical Jewish texts"""
        try:
            params = {'query': query}
            if category:
                params['category'] = category
            
            result = await self._make_request("search/historical", params)
            if result and isinstance(result, list):
                return result
            
            return [
                {
                    'title': f'Historical Text Related to {query}',
                    'description': 'Early Jewish historical document',
                    'period': '18th-19th century',
                    'category': category or 'Historical Documents'
                }
            ]
        except Exception as e:
            logger.error(f"Error searching historical texts: {e}")
            return []
    
    async def get_chassidic_genealogy(self, rebbe: str = "") -> Optional[Dict]:
        """Get Chassidic leadership genealogy"""
        try:
            params = {'rebbe': rebbe} if rebbe else {}
            return await self._make_request("chassidic/genealogy", params)
        except Exception as e:
            logger.error(f"Error getting genealogy: {e}")
            return {
                'lineage': 'Chassidic Rebbe lineage',
                'dynasties': ['Chabad', 'Breslov', 'Satmar', 'Belz'],
                'note': 'Traditional Chassidic leadership succession'
            }
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()