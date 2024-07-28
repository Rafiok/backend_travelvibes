from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from .serializers import *
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
import json
from django.db.models import F
from haversine import haversine
from django.utils import timezone
from .constants import *
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
import requests
from .models import l, p


# Create your views here.

def createLieu(data : dict) -> Lieu :
    return Lieu.objects.create(nom = data['name'], latitude = data['lat'], longitude = data['lng'])

def send_to_channel(channel_name : str, obj, type = 'echo') :
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(channel_name, {
                'type' : type,
                'result' : obj
            })



@api_view(['POST'])
def charge_file(request):
    file = request.FILES.get('file',None)
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
    nom = request.data.get('name')
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
            'access' : refresh.token
        }
    })
    
@api_view(['POST', 'GET'])
def get_voyages(request) :
    excepts = json.loads(request.data.get('excepts')) 
    
    try :
        depart = json.loads(request.data.get('depart'))
        arrivee = json.loads(request.data.get('arrivee'))
        date = datetime.strptime(request.data.get('date'), "%Y-%m-%dT%H:%M:%S")
        
        """ voyages = VoyagePrevu.objects.filter(
            date_depart__lt=date + timezone.timedelta(minutes=APPROX_TIME),
            date_depart__gt=date - timezone.timedelta(minutes=APPROX_TIME)
        ).annotate(
            coeff=(
                haversine(
                    (F('lieux_depart__latitude'), F('lieux_depart__longitude')),
                    (depart['lat'], depart['lng'])
                ) +
                haversine(
                    (F('lieux_darrive__latitude'), F('lieux_darrive__longitude')),
                    (arrivee['lat'], arrivee['lng'])
                )
            )
        ).order_by('-coeff') """

        voyages = VoyagePrevu.objects.all().exclude(voyage__voyage_correspondant__user__pk = request.user.pk)
        voys = []
        for voy in voyages :
            voys.append({
                'voy' : voy,
                'coeff' : haversine(
                    (voy.lieux_depart.latitude, voy.lieux_depart.longitude),
                    (depart['lat'], depart['lng'])
                ) +
                haversine(
                    (voy.lieux_arrive.latitude, voy.lieux_arrive.longitude),
                    (arrivee['lat'], arrivee['lng'])
                )
            })
        print(voys)
        voys.sort(key=lambda e : e['coeff'])
        voyages = [vs['voy'] for vs in voys ]
    except Exception as e :
        print(e)
        voyages = VoyagePrevu.objects.all().order_by('-created_at')
    total_count = len(voyages)
    
    return Response({
        'done' : True,
        'result' : VoyageSerializer([ v for v in voyages if not v.pk in excepts ][:PAGINATION_SIZE], many = True).data,
        'other' : total_count
    })

@api_view(["GET"])
def search_place(request, name):
    req = requests.get(
        f'https://maps.googleapis.com/maps/api/place/textsearch/json?key=AIzaSyDNoBJJXRj_p5miy5gSPGazRa4Mr-95D18&query={name}')
    results = json.loads(req.content)['results']
    return Response({
        'done': True,
        'result': results
    })

@api_view(["GET", "POST"])
def get_details(request) :
    key = request.data.get('key')
    return Response({
        'done' : True,
        'result' : json.loads(g_v(key))
    })

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def create_voyage(request) :
    depart = json.loads(request.data.get('depart'))
    arrivee = json.loads(request.data.get('arrivee'))
    places = int(request.data.get('places'))
    price = int(request.data.get('price'))
    date = datetime.strptime(request.data.get('date'), "%Y-%m-%dT%H:%M:%S")
    voy = VoyagePrevu.objects.create( lieux_depart = createLieu(depart), lieux_arrive = createLieu(arrivee), user = request.user, date_depart = date, price = price, places_number = places )
    return Response({
        'done' : True,
        'result' : voy.pk
    })
    
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def create_dem(request) :
    pk = int(request.data.get('pk'))
    voyage_prevu = VoyagePrevu.objects.get(pk = pk)
    voyage = Voyage.objects.create(voyageur = request.user, lieux_depart = voyage_prevu.lieux_depart, lieux_arrive = voyage_prevu.lieux_arrive, date_depart = voyage_prevu.date_depart, voyage_correspondant = voyage_prevu)
    return Response({
        'done' : True,
        'result' : voyage.pk
    })


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def get_requetes(request) :
    demandes = request.user.voyages.all().order_by('-created_at')
    offres = Voyage.objects.filter(voyage_correspondant__user__pk = request.user.pk ).order_by('-created_at')

    return Response({
        'done' : True,
        'result' : {
            'demandes' : RequeteSerializer(demandes, many = True).data,
            'offres' : RequeteSerializer(offres, many = True).data
        }
    })

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def init_chat(request, pk) :
    requete = Voyage.objects.get(pk = pk)
    return Response({
        'done' : True,
        'result' : {
            'user' : UserVoyageSerializer(request.user).data,
            'requete' : RequeteSerializer(requete).data,
            'messages' : MessageSerializer(requete.messages.all().order_by('-created_at'), many = True).data 
        }
    })

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def set_decision(request) :
    req= int( request.data.get('req'))
    decision = request.data.get('decision')
    requete = Voyage.objects.get(pk = req)
    portefeuille_voyageur = Portefeuille.objects.get_or_create(user = requete.voyageur)[0]
    portefeuille_conducteur = Portefeuille.objects.get_or_create(user = requete.voyage_correspondant.user)[0]
    if decision == 'accepted' :
        if not portefeuille_voyageur.can_pay(requete.voyage_correspondant.price) :
            return Response({
                'done' : False
            })
        requete.state = 'accepté'

        Transaction.objects.create(portefeuille = portefeuille_conducteur, amount = requete.voyage_correspondant.price, transaction_id = 'forreq' + str(requete.id))
        Transaction.objects.create(portefeuille = portefeuille_voyageur, amount = -requete.voyage_correspondant.price, transaction_id = 'forreq' + str(requete.id))
    elif decision == 'refused' :
        requete.state = 'refusé'
    elif decision == 'finilized' :
        requete.payed = True
        requete.state = 'finalisé'
        transs = Transaction.objects.filter(transaction_id = 'forreq' + str(requete.id))
        for t in transs :
            if t.portefeuille.user == requete.voyageur.id :
                t.typ = 'Payé'
            else :
                t.typ = 'Encaissé'
            t.save()
        
    else :
        OurDetails.objects.create(key = 'launch:' + str(requete.pk), value= 'yes')
    requete.save()
    send_to_channel('req.' + str(requete.pk), RequeteSerializer(requete).data)
    m = Message.objects.create(user = request.user, text = g_v('default:decision:' + decision ).format(request.user.nom if request.user.nom else "l'utilisateur"), voyage = requete, typ = 'info')
    send_to_channel('req.' + str(requete.pk), MessageSerializer(m).data, 'message')
    return Response({
        'done' : True,
    })

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def charg_files(request) :
    file = request.FILES.get('file')
    image = Image.objects.create(name="message", file = file)

    return Response({
        'done' : True,
        'result' : image.pk
    })

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def init_portefeuille(request) :
    return Response({
        'done' : True,
        'result' : PortefeuilleSerializer(Portefeuille.objects.get_or_create(user = request.user)[0]).data,
        'oth' : g_v('whatsapp:link'),
        'api_link' : g_v('kkiapay:public')
    })

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def create_transaction(request) :
    porte = Portefeuille.objects.get_or_create(user = request.user)[0]
    transaction = Transaction.objects.create(portefeuille = porte, amount = int(request.data.get('amount')), typ = request.data.get('typ'), transaction_id = request.data.get('transaction_id'))
    return Response({
        'done' : True,
        'result' : PortefeuilleSerializer(porte).data
    })


@api_view(['GET', 'HEAD'])
@permission_classes([IsAuthenticated])
def ping(request):
    return Response({'done': True})

@api_view(['GET', 'HEAD'])
@permission_classes([IsAuthenticated])
def get_pubs(request) :
    pubs = request.user.voyage_prevus.all().order_by('-created_at')

    return Response({
        'done' : True,
        'result' : VoyageSerializer(pubs, many = True).data,
        'other' : len(pubs)
    })