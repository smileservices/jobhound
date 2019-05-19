import requests
from random import randint
import time, datetime
import logging

class CustomSession:
    res_time = []

    def __init__(self, logger_name):
        self.session = requests.Session()
        self.logger = logging.getLogger(logger_name)

    def get(self, url, throttle=False):
        '''
        throttle - time interval (s, s)
        '''
        if throttle:
            throttle = randint(*throttle)
            time.sleep(throttle)
        result = self.session.get(url)
        self.res_time.append(result.elapsed.microseconds / 1000)
        self.log(throttle, result)
        return result

    def log(self, throttle, result):
        entry = {
            'date_time': datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            'url': result.url,
            'throttle': throttle,
            'code': result.status_code,
            'time': result.elapsed.microseconds / 1000,
        }
        self.logger.info(entry)
