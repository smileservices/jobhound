import aiohttp
import asyncio
from random import randint
import time, datetime
import logging


class AsyncSession:
    res_time = []

    def __init__(self, session, logger_name):
        self.session = session
        self.logger = logging.getLogger(logger_name)

    async def get(self, url, throttle=(0, 0)):
        '''
        throttle - time interval (s, s)
        '''
        if throttle != (0, 0):
            throttle = randint(*throttle)
            await asyncio.sleep(throttle)
        t0 = datetime.datetime.now()
        result = await self.session.get(url)
        result.elapsed = datetime.datetime.now() - t0
        self.log(throttle, result)
        return await result.text()

    def log(self, throttle, result):
        entry = {
            'date_time': datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            'url': result.url,
            'throttle': throttle,
            'code': result.status,
            'time': result.elapsed,
        }
        self.logger.info(entry)
