import logging
import environ
from elasticsearch import Elasticsearch

from truelancer_bowl import TruelancerBowl
from logger import create_logger
from session import CustomSession
from storage.elasticsearch import ElasticSearchStorage

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)
# reading .env file
environ.Env.read_env('../.env')

create_logger('crawler', env.str('CRAWLER_LOG'), logging.DEBUG)
logger = logging.getLogger('crawler')
logger.info('Starting the app...')

elastic_conn = Elasticsearch()
storages = {}
sessions = {}
crawlers = {}

######
#
# Set up crawlers
#
###

logger.info('setting up truelancer crawler...')
truelancer_elastic_storage_obj_settings_dict = {
    'doc_type': TruelancerBowl.doc_type,
    'settings': {
        'number_of_shards': 1,
    },
    'connection': elastic_conn,
    'mappings': TruelancerBowl.elasticsearch_get_setup_settings()
}
storages['truelancer'] = ElasticSearchStorage(
    'truelancer',
    truelancer_elastic_storage_obj_settings_dict,
    logger_name= 'crawler'
)

sessions['truelancer'] = CustomSession(logger_name='crawler')

crawlers['truelancer'] = TruelancerBowl(
    storages['truelancer'],
    sessions['truelancer'],
    logger_name='crawler'
)

######
#
# Start crawlers
#
###

for name,crawler in crawlers.items():
    crawler.start()
