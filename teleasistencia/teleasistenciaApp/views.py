from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from rest_framework.utils import json
from social_django.models import UserSocialAuth
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.decorators import parser_classes

# Create your views here.
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.decorators import parser_classes




def index(request):
    context = {}
    if request.user.is_authenticated:
        uidmio = request.user.email
        #Borrar, ya no hay social auth
        #token = get_object_or_404(UserSocialAuth, uid=uidmio)
        #context['token'] = token.extra_data
    return render(request, 'teleasistenciaIndex.html', context)
