from rest_framework import viewsets, response
from rest_framework.generics import ListAPIView

from jobhound.retrieve.elastic import ElasticInterface
from jobhound.rest.serializers import JobSerializer, JobSuggestSerializer


class JobViewSet(viewsets.ViewSet):
    serializer_class = JobSerializer

    def list(self, request):
        el_int = ElasticInterface('_job')
        size = request.query_params.get('size')
        if 'term' in request.query_params:
            records = el_int.search(request.query_params['term'], size)
            serializer = JobSerializer(
                instance=records,
                many=True
            )
        elif 'prefix' in request.query_params:
            records = el_int.suggest(request.query_params['prefix'])
            serializer = JobSuggestSerializer(
                instance=records,
                many=True
            )
        else:
            records = el_int.latest(size)
            serializer = JobSerializer(
                instance=records,
                many=True
            )
        return response.Response(serializer.data)
