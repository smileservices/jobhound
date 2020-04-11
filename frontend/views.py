from django.shortcuts import render
from django.http import request, response
from django.contrib.auth.decorators import login_required

# Create your views here.


def homepage(request):
    return render(request, 'frontend/homepage.html')