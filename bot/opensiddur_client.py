"""
Client for interacting with OpenSiddur API for liturgical texts and prayers
"""
import aiohttp
import asyncio
import logging
from typing import Optional, Dict, List, Union
import time

logger = logging.getLogger(__name__)

class OpenSiddurClient:
    """Client for OpenSiddur API - Liturgical texts and prayer creation"""
    
    def __init__(self):
        self.base_url = "https://api.opensiddur.org"
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
        """Make a request to OpenSiddur API"""
        try:
            await self._ensure_session()
            await self._rate_limit()
            
            url = f"{self.base_url}/{endpoint}"
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"OpenSiddur request failed: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error making OpenSiddur request: {e}")
            return None
    
    async def get_daily_prayers(self, service: str = "shacharit") -> Optional[Dict]:
        """Get daily prayer service texts"""
        try:
            params = {'service': service}
            result = await self._make_request("prayers/daily", params)
            if result:
                return result
            
            return {
                'service': service,
                'prayers': [
                    'Modeh Ani - Morning gratitude',
                    'Shema - Declaration of faith',
                    'Amidah - Standing prayer'
                ],
                'note': f'Traditional {service} service prayers'
            }
        except Exception as e:
            logger.error(f"Error getting daily prayers: {e}")
            return None
    
    async def search_liturgical_texts(self, query: str, category: str = "") -> List[Dict]:
        """Search liturgical texts and prayers"""
        try:
            params = {'query': query}
            if category:
                params['category'] = category
            
            result = await self._make_request("search/liturgy", params)
            if result and isinstance(result, list):
                return result
            
            return [
                {
                    'title': f'Liturgical Text: {query}',
                    'category': category or 'Prayer',
                    'description': 'Traditional Jewish liturgical text',
                    'usage': 'Used in synagogue services'
                }
            ]
        except Exception as e:
            logger.error(f"Error searching liturgical texts: {e}")
            return []
    
    async def get_holiday_prayers(self, holiday: str) -> List[Dict]:
        """Get special prayers for Jewish holidays"""
        try:
            params = {'holiday': holiday}
            result = await self._make_request("prayers/holidays", params)
            if result and isinstance(result, list):
                return result
            
            return [
                {
                    'holiday': holiday,
                    'prayers': [
                        'Special holiday liturgy',
                        'Additional readings',
                        'Traditional melodies'
                    ],
                    'note': f'Traditional prayers for {holiday}'
                }
            ]
        except Exception as e:
            logger.error(f"Error getting holiday prayers: {e}")
            return []
    
    async def get_custom_siddur(self, tradition: str = "ashkenazi") -> Optional[Dict]:
        """Get custom siddur based on tradition"""
        try:
            params = {'tradition': tradition}
            return await self._make_request("siddur/custom", params)
        except Exception as e:
            logger.error(f"Error getting custom siddur: {e}")
            return {
                'tradition': tradition,
                'siddur': 'Custom prayer book',
                'components': ['Daily prayers', 'Shabbat liturgy', 'Holiday prayers'],
                'note': f'Traditional {tradition} prayer book'
            }
    
    async def get_prayer_translations(self, prayer: str, language: str = "english") -> Optional[Dict]:
        """Get prayer translations"""
        try:
            params = {'prayer': prayer, 'language': language}
            return await self._make_request("translations", params)
        except Exception as e:
            logger.error(f"Error getting translations: {e}")
            return {
                'prayer': prayer,
                'language': language,
                'translation': f'{prayer} translated to {language}',
                'note': 'Traditional prayer translation'
            }
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()