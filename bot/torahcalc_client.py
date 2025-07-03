"""
Client for interacting with TorahCalc API for biblical calculations
"""
import aiohttp
import asyncio
import logging
from typing import Optional, Dict, List, Union
import time

logger = logging.getLogger(__name__)

class TorahCalcClient:
    """Client for TorahCalc API - Biblical calculations and measurements"""
    
    def __init__(self):
        self.base_url = "https://api.torahcalc.com"
        self.session = None
        self.last_request_time = 0
        self.rate_limit_delay = 1.0  # 1 second between requests
    
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
        """Make a request to TorahCalc API"""
        try:
            await self._ensure_session()
            await self._rate_limit()
            
            url = f"{self.base_url}/{endpoint}"
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"TorahCalc request failed: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error making TorahCalc request: {e}")
            return None
    
    async def calculate_biblical_measurement(self, measurement: str, value: float) -> Optional[Dict]:
        """Calculate biblical measurements (cubits, shekels, etc.)"""
        try:
            params = {
                'measurement': measurement,
                'value': value
            }
            return await self._make_request("convert", params)
        except Exception as e:
            logger.error(f"Error calculating measurement: {e}")
            return {
                'input': f"{value} {measurement}",
                'conversions': {
                    'modern_equivalent': f"Approximately {value * 0.5} meters" if measurement == "cubit" else f"{value} units",
                    'description': f"Biblical {measurement} measurement"
                }
            }
    
    async def get_biblical_calendar_calculation(self, year: int) -> Optional[Dict]:
        """Get biblical calendar calculations"""
        try:
            params = {'year': year}
            return await self._make_request("calendar", params)
        except Exception as e:
            logger.error(f"Error getting calendar: {e}")
            return {
                'year': year,
                'info': 'Biblical calendar calculations for Sabbatical and Jubilee years'
            }
    
    async def calculate_torah_gematria(self, text: str) -> Optional[Dict]:
        """Calculate advanced gematria values"""
        try:
            params = {'text': text}
            return await self._make_request("gematria", params)
        except Exception as e:
            logger.error(f"Error calculating gematria: {e}")
            # Fallback calculation
            hebrew_values = {
                'א': 1, 'ב': 2, 'ג': 3, 'ד': 4, 'ה': 5, 'ו': 6, 'ז': 7, 'ח': 8, 'ט': 9,
                'י': 10, 'כ': 20, 'ל': 30, 'מ': 40, 'נ': 50, 'ס': 60, 'ע': 70, 'פ': 80, 'צ': 90,
                'ק': 100, 'ר': 200, 'ש': 300, 'ת': 400, 'ך': 20, 'ם': 40, 'ן': 50, 'ף': 80, 'ץ': 90
            }
            total = sum(hebrew_values.get(char, 0) for char in text)
            return {
                'text': text,
                'standard_value': total,
                'calculation_type': 'standard_gematria'
            }
    
    async def get_temple_measurements(self) -> Optional[Dict]:
        """Get information about Temple measurements"""
        try:
            return await self._make_request("temple")
        except Exception as e:
            logger.error(f"Error getting temple measurements: {e}")
            return {
                'temple': 'Second Temple',
                'measurements': {
                    'length': '100 cubits',
                    'width': '100 cubits',
                    'height': '100 cubits'
                },
                'note': 'Measurements based on Talmudic sources'
            }
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()