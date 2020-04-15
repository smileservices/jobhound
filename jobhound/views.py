from rest_framework import viewsets, response
from rest_framework.permissions import IsAuthenticated

from jobhound.retrieve.elastic import ElasticInterface
from jobhound.rest.serializers import JobSerializer, JobSuggestSerializer


class JobViewSet(viewsets.ViewSet):
    serializer_class = JobSerializer
    permission_classes = (IsAuthenticated,)
    
    def list(self, request):
        el_int = ElasticInterface('_job')
        page = int (request.query_params['page'] if 'page' in request.query_params else 0)
        if 'prefix' in request.query_params:
            records = el_int.suggest(request.query_params['prefix'])
            serializer = JobSuggestSerializer(
                instance=records,
                many=True
            )
            data = serializer.data
        else:
            if 'term' in request.query_params:
                result = el_int.search(request.query_params['term'], page)
            else:
                result = el_int.latest(page)
            serialized_items = JobSerializer(
                instance=result['items'],
                many=True
            )
            data = {
                'items': serialized_items.data,
                'stats': result['stats']
            }

        return response.Response(data)
