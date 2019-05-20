from django.db import models
from api_user.models import ApiUser
import secrets


# Create your models here.

class APIKey(models.Model):
    user = models.ForeignKey(ApiUser, on_delete=models.CASCADE)
    api_key = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)

    @staticmethod
    def generate_key():
        key = secrets.token_urlsafe(16)
        return key
    
    def __unicode__(self):
        return self.api_key
