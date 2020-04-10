import logging
import environ
from elasticsearch import Elasticsearch
import asyncio
import aiohttp

from async_truelancer import AsyncTruelancerBowl
from async_pythonjobs import AsyncPythonJobsBowl
from core.async_abstract_bowl import AsyncAbstractBowl
from logger import create_logger
from async_session import AsyncSession
from storage.elasticsearch import ElasticSearchStorage
from storage.mock import MockStorage

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

# reading .env file
environ.Env.read_env('../.env')

create_logger('truelancer', env.str('CRAWLER_LOG'), logging.DEBUG)
create_logger('pythonjobs', env.str('CRAWLER_LOG'), logging.DEBUG)

logger = logging.getLogger('async_crawler')
logger.info('Starting the app...')


elastic_conn = Elasticsearch()
storages = {}
sessions = {}
crawlers = {'truelancer': AsyncTruelancerBowl, 'pythonjobs': AsyncPythonJobsBowl}
# crawlers = {'truelancer': AsyncTruelancerBowl}

######
#
# Set up crawlers
#
###

logger.info('setting up truelancer crawler...')
truelancer_elastic_storage_obj_settings_dict = {
    'doc_type': AsyncTruelancerBowl.doc_type,
    'settings': {
        'number_of_shards': 1,
    },
    'connection': elastic_conn,
    'mappings': AsyncTruelancerBowl.elasticsearch_get_setup_settings()
}
storages['truelancer'] = ElasticSearchStorage(
    'truelancer',
    truelancer_elastic_storage_obj_settings_dict,
    logger_name= 'truelancer'
)


logger.info('setting up pythonjobs crawler...')
pythonjobs_elastic_storage_obj_settings_dict = {
    'doc_type': AsyncPythonJobsBowl.doc_type,
    'settings': {
        'number_of_shards': 1,
    },
    'connection': elastic_conn,
    'mappings': AsyncPythonJobsBowl.elasticsearch_get_setup_settings()
}

storages['pythonjobs'] = ElasticSearchStorage(
    'pythonjobs',
    pythonjobs_elastic_storage_obj_settings_dict,
    logger_name= 'pythonjobs'
)

######
#
# Start crawlers
#
###

async def prepare_crawler(name: str, crawler_class: AsyncAbstractBowl, loop, connector):
    async with aiohttp.ClientSession(loop=loop, connector=connector) as session:
        async_session = AsyncSession(session=session, logger_name=name)
        crawler = crawler_class(storages[name], async_session, name)
        return await crawler.start()
         

async def main():
    tasks = []
    connector = aiohttp.TCPConnector()
    loop = asyncio.get_event_loop()
    for name, crawler in crawlers.items():
        tasks.append(asyncio.create_task(
            await prepare_crawler(name=name, crawler_class=crawler, loop=loop, connector=connector)
        ))
    await asyncio.gather(*tasks)


async def test():
    await asyncio.gather(
        asyncio.create_task(await prepare_crawler(name='pythonjobs', crawler_class=AsyncPythonJobsBowl))
    )
    

if __name__ == '__main__':
    asyncio.run(main())
