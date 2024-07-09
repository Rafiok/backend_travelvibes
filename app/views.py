from django.shortcuts import render
from rest_framework.decorators import api_view
from .serializers import *
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken


# Create your views here.

@api_view(['POST'])
def charge_file(request):
    file = request.POST.get('file',None)
    img = Image.objects.create(file = file)

    return Response({
        'done' : True,
        'result' : ImageSerializer(img).data
    })

@api_view(['POST'])
def register_user(request) :
    ident = request.data.get('ident')
    password = request.data.get('password')
    img = int(request.data.get('img'))
    nom = request.data.get('nom')
    sex = request.data.get('sex')

    if User.objects.filter(username = ident) : return Response({
        'done' : False
    })
    
    user = User.objects.create_user(email = (ident if "@" in ident else None), number = (ident if "@" not in ident else None) ,password = password, username = ident, nom = nom, sex = sex )
    if img :
        user.profil = Image.objects.get(pk = img)
        user.save()

    refresh = RefreshToken.for_user(user)

    return Response({
        'done' : True, 
        'result' : {
            'refresh' : str(refresh),
            'access' : refresh.access_token
        }
    })
    


