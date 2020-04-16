from elasticsearch import Elasticsearch
from jobhound.exceptions import NoIndicesFound
from django.conf import settings


class ElasticInterface:

    def __init__(self, suffix):
        self.es = Elasticsearch()
        self.indexes = []
        for idx in self.es.indices.get_alias():
            if suffix == idx[-len(suffix):]:
                self.indexes.append(idx)
        if len(self.indexes) == 0:
            raise NoIndicesFound

    def search(self, term, page=0):
        page_size = settings.ELASTICSEARCH['PAGE_SIZE']
        page_offset = page * page_size
        q = {
            "from": page_offset,
            "size": page_size,
            "sort": {
                "date": {"order": "desc", "missing": "_last", "unmapped_type": "long"}
            },
            "query": {
                "multi_match": {
                    "query": term,
                    "fields": ["title", "description", "skills", "location"],
                    "fuzziness": 1
                }
            }
        }
        res = self.es.search(self.indexes, body=q)
        extracted_response = self.extract_results(res, 'search')
        extracted_response['stats']['page_size'] = page_size
        return extracted_response

    def suggest(self, prefix):
        q = {
            "suggest": {
                "job-suggest": {
                    "prefix": prefix,
                    "completion": {
                        "field": "suggest",
                        "size": 5
                    }
                }
            }
        }
        res = self.es.search(self.indexes, body=q)
        return self.extract_results(res, 'suggest')

    def latest(self, page):
        page_size = settings.ELASTICSEARCH['PAGE_SIZE']
        page_offset = page * page_size
        q = {
            "from": page_offset,
            "size": page_size,
            "sort": [
                {"date": {"order": "desc", "missing": "_last", "unmapped_type": "long"}},
            ]
        }
        res = self.es.search(self.indexes, body=q)
        extracted_response = self.extract_results(res, 'search')
        extracted_response['stats']['page_size'] = page_size
        return extracted_response

    def extract_results(self, res, type):
        extracted = False
        if type == 'search':
            results = [r['_source'] for r in res['hits']['hits']]
            extracted = {
                'items': results,
                'stats': {
                    'total': res['hits']['total']['value'],
                    'count': len(results)
                }
            }
        elif type == 'suggest':
            extracted = [{'text': r['text'], 'title': r['_source']['title']} for r in
                         res['suggest']['job-suggest'][0]['options']]
        return extracted
