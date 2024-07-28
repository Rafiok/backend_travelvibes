from rest_framework import serializers
from .models import *

class ImageSerializer(serializers.ModelSerializer) :

    class Meta :
        model = Image
        fields = ('id', 'name', 'url')

class UserVoyageSerializer(serializers.ModelSerializer) :

    class Meta :
        model = User
        fields = ('id', 'nom', 'get_profil', 'get_feedbacks', 'user_feeds')

class LieuSerializer(serializers.ModelSerializer) :

    class Meta :
        model = Lieu
        fields = ('id', 'nom')

class VoyageSerializer(serializers.ModelSerializer) :
    user = UserVoyageSerializer()
    lieux_depart = LieuSerializer()
    lieux_arrive = LieuSerializer()

    class Meta :
        model = VoyagePrevu
        fields = ('id', 'user', 'lieux_depart', 'lieux_arrive', 'date_depart', 'price', 'places_number')

class MessageSerializer(serializers.ModelSerializer) :
    user = UserVoyageSerializer()
    
    class Meta :
        model = Message
        fields = ('id', 'user', 'text', 'get_image', 'get_audio', 'created_at', 'typ',)

class RequeteSerializer(serializers.ModelSerializer) :
    voyageur = UserVoyageSerializer()
    lieux_depart = LieuSerializer()
    lieux_arrive = LieuSerializer()
    voyage_correspondant = VoyageSerializer()
    last_message = MessageSerializer()
    class Meta : 
        model = Voyage
        fields = ('id', 'voyageur', 'lieux_depart', 'lieux_arrive', 'date_depart', 'state', 'voyage_correspondant', 'has_accepted',  'payed', 'last_message')

class TransactionSerializer(serializers.ModelSerializer) :
    class Meta :

        model = Transaction
        fields = ('id', 'created_at', 'amount', 'typ')

class PortefeuilleSerializer(serializers.ModelSerializer) :
    user = serializers.IntegerField(source="user.pk")
    transactions = TransactionSerializer(many = True)
    class Meta :
        model = Portefeuille
        fields = ('id', 'user', 'get_amount', 'transactions')
        