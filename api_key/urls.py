from django.urls import path, reverse_lazy
from api_key.views import ApiKeyUpdate

urlpatterns = [
    path('update', ApiKeyUpdate.as_view(success_url=reverse_lazy('api_user-profile')),
         name='api_key_update'),
]
