import logging


class ElasticSearchStorage:
    idx_links_crawled = ""
    es = None

    def __init__(self, idx_prefix, settings, logger_name):
        '''
        :param idx_prefix: index name
        :param settings: settings for building the index (mapping, analyze)
        '''
        self.logger = logging.getLogger(logger_name)

        self.es = settings['connection']
        self.idx_prefix = idx_prefix
        self.idx_links_crawled = self.index_name("links_crawled")
        self.idx = self.index_name(settings['doc_type'])

        if not self.es.indices.exists(self.idx):
            self.logger.warning('{} index not found! Creating it...'.format(self.idx_prefix))
            # create main index
            idx_body = {
                'settings': settings['settings'],
                'mappings': settings['mappings']
            }
            if 'analyzer' in settings:
                idx_body['settings']['analyzer'] = settings['analyzer']
            self.es.indices.create(self.idx, body=idx_body)
            self.logger.info(
                'Elasticsearch index {} created successfully! Creating links index also...'.format(self.idx))
            # recreate links indices
            self.es.indices.delete(index=self.idx_links_crawled, ignore=[400, 404])
            idx_links_body = {'settings': {}, 'mappings': {}}
            idx_links_body['settings']['number_of_shards'] = 1
            idx_links_body['mappings'] = {
                'properties': {
                    'url': {'type': 'keyword'},
                    'date': {'type': 'date', 'format': 'date_hour_minute_second'},
                    'status': {'type': 'keyword'},
                }
            }
            self.es.indices.create(self.idx_links_crawled, body=idx_links_body)
            self.logger.info('{} elastic search index created successfully!'.format(self.idx_links_crawled))

    def index_name(self, name):
        return '{}_{}'.format(self.idx_prefix, name)

    def get_index_name(self):
        return self.idx

    def record_exists(self, index, field, value):
        q = {
            'size': 0,
            'query': {
                'bool': {
                    'filter': {
                        'term': {field: value}
                    }
                }
            }
        }
        res = self.es.search(self.index_name(index), q)
        return res['hits']['total']['value'] != 0

    def filter(self, index_name, filter_list):
        query = {
            'query': {
                'bool': {
                    'filter': [f for f in filter_list]
                }
            }
        }
        q_res = self.es.search(index=self.index_name(index_name), body=query)
        return self.get_results_iterator(q_res)

    def search(self, index_name, query):
        query = {
            'query': {
                'bool': {}
            }
        }
        pass

    def save(self, index_name, obj, id=None):
        self.es.index(index=self.index_name(index_name), doc_type='_doc', id=id, body=obj)

    @staticmethod
    def get_results_iterator(q_res):
        for i in range(len(q_res['hits']['hits'])):
            yield q_res['hits']['hits'][i]['_source']
