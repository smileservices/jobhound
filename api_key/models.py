from django.db import models
from api_user.models import ApiUser


# Create your models here.

class APIKey(models.Model):
    user = models.ForeignKey(ApiUser, on_delete=models.CASCADE)
    api_key = models.CharField(max_length=128)
