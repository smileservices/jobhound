from django.forms import ModelForm
from api_key.models import APIKey


class ApiKeyForm(ModelForm):
    class Meta:
        model = APIKey
        fields = ('api_key',)
