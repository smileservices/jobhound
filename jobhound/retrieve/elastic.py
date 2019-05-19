from elasticsearch import Elasticsearch
from jobhound.exceptions import NoIndicesFound


class ElasticInterface:

    def __init__(self, suffix):
        self.es = Elasticsearch()
        self.indexes = []
        for idx in self.es.indices.get_alias():
            if suffix == idx[-len(suffix):]:
                self.indexes.append(idx)
        if len(self.indexes) == 0:
            raise NoIndicesFound

    def search(self, term, size=10):
        q = {
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
        res = self.es.search(self.indexes, body=q, size=size)
        return self.extract_results(res, 'search')

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

    def latest(self, size=10):
        q = {
            "sort": [
                {"date": {"order": "asc", "missing": "_last", "unmapped_type": "long"}},
            ]
        }
        res = self.es.search(self.indexes, body=q, size=size)
        return self.extract_results(res, 'search')

    def extract_results(self, res, type):
        extracted = False
        if type == 'search':
            extracted = [r['_source'] for r in res['hits']['hits']]
        elif type == 'suggest':
            extracted = [{'text': r['text'], 'title': r['_source']['title']} for r in
                         res['suggest']['job-suggest'][0]['options']]
        return extracted
