from rest_framework import serializers


class JobSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=256)
    description = serializers.CharField()
    skills = serializers.ListField()
    url = serializers.CharField()
    location = serializers.CharField()
    date = serializers.DateTimeField(required=False)


class JobSuggestSerializer(serializers.Serializer):
    text = serializers.CharField()
    title = serializers.CharField()
