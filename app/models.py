from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
import os
import json
from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

def calculate_resp_time(requete, user) :
    messages = requete.messages.all().filter(user__pk = user.pk)

def p(obj) :
    return json.dumps(obj)

l = lambda e: json.loads(e)

ENDPOINT = os.environ.get('ENDOINT', 'http://localhost:8080')

# Create your models here.

class OurDetails(models.Model) :
    key = models.CharField(max_length=150)
    value = models.TextField()

def g_v(key : str) :
    return OurDetails.objects.get(key = key).value


class CustomUserManager(BaseUserManager): 
    def create_user(self, password, **extra_fields):
        """ if not (email ):
            raise ValueError("l'email ou le numéro ne peuvent etre nulls") """
        
        user = self.model( **extra_fields)    
        user.set_password(password)
        user.save()
        return user
    def create_superuser(self,password, **extra_fields):
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_superuser',True)
        extra_fields.setdefault('is_active',True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError("Le Super utilisateur doit forcément avoir la variable is_staf à True")
        
        if extra_fields.get('is_superuser') is not True:

            raise ValueError("Le Super utilisateur doit forcément avoir la variable is_superuser à True")
        return self.create_user( password, **extra_fields)

class Image(models.Model) :
    name = models.CharField(default='profil', max_length=500)
    file = models.ImageField(upload_to="images/")

    def __str__(self) -> str:
        return self.name
    
    def url(self) :
        return self.file.url
    
class Audio(models.Model) :
    name = models.CharField(default='profil', max_length=500)
    file = models.ImageField(upload_to="audio/")

    def __str__(self) -> str:
        return self.name
    
    def url(self) :
        return self.file.url

class User(AbstractBaseUser,PermissionsMixin):
    nom = models.CharField(max_length= 150, blank= True, null= True)
    number = models.CharField(max_length= 150, null=True, blank=True )
    sex= models.CharField(max_length=50, null=True, blank=True)
    whatsapp = models.CharField(max_length= 150, blank= True, null= True)
    email = models.EmailField(null=True, blank= True) 
    is_staff = models.BooleanField(default= False)
    is_active = models.BooleanField(default= True)
    objects = CustomUserManager() 
    created_at = models.DateTimeField(auto_now_add = True)
    username = models.CharField(max_length=150, unique=True, default='user')
    profil = models.ForeignKey(Image, related_name="users", on_delete=models.SET_NULL, null=True, blank=True)
    REQUIRED_FIELDS = []
    USERNAME_FIELD = "username"

    def get_profil(self) :
        return self.profil.url() if self.profil else g_v('profil:default')

    def get_feedbacks(self) :
        cpt = 0
        for feed in self.feedbacks.all() : cpt += feed/self.feedbacks.count()
        return int(cpt)

    def __str__(self) -> str:
        return f"{self.nom if self.nom else self.username}"
    
    def user_feeds(self) :
        return self.feedbacks.count()

    


class FeedBack(models.Model) :
    user = models.ForeignKey(User, related_name="feedbacks", on_delete=models.CASCADE, null=True, blank=True)
    value = models.IntegerField(default=7)
    text = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name="my_feedbacks", on_delete=models.CASCADE, null=True, blank=True)





class Lieu(models.Model):
    nom =  models.CharField(max_length= 150, blank= True, null= True)
    latitude = models.FloatField(blank= True, null= True)
    longitude = models.FloatField(blank= True, null= True)
    details = models.TextField(null=True, blank=True)
    def __str__(self) -> str:
        return self.nom
    
    

class VoyagePrevu(models.Model):
    user = models.ForeignKey(User, on_delete= models.CASCADE, related_name= "voyage_prevus")  
    
    lieux_depart = models.ForeignKey(Lieu, on_delete= models.SET_NULL, related_name= "voyages_depart_prevu", blank= True, null= True)

    lieux_arrive = models.ForeignKey(Lieu, on_delete= models.SET_NULL, related_name= "voyages_arrive_prevu", blank= True, null= True)

    date_depart = models.DateTimeField(blank= True, null= True)

    price = models.IntegerField(null=True, blank=True)

    places_number = models.IntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)


class Voyage(models.Model):
    voyageur = models.ForeignKey(User, on_delete= models.CASCADE, related_name= "voyages", blank= True, null= True) 

    lieux_depart = models.ForeignKey(Lieu, on_delete= models.SET_NULL, related_name= "voyages_depart", blank= True, null= True)

    lieux_arrive = models.ForeignKey(Lieu, on_delete= models.SET_NULL, related_name= "voyages_arrives", blank= True, null= True)

    date_depart = models.DateTimeField(blank= True, null= True)
    
    state = models.CharField(max_length= 50, default= "en attente")

    voyage_correspondant = models.OneToOneField(VoyagePrevu, models.SET_NULL, blank= True, null= True)

    created_at = models.DateTimeField(auto_now_add=True)

    payed = models.BooleanField(default=False)
    
    def has_accepted(self) :
        return OurDetails.objects.filter(key = 'launch:' + str(self.pk)).exists()
    
    def last_message(self) :
        return self.messages.all().order_by('-created_at')[0] if self.messages.all().count() else Message.objects.filter(text = g_v('default:message:text'))[0]
    
class Message(models.Model):

    user = models.ForeignKey(User, related_name= "messages",on_delete= models.CASCADE,blank= True, null= True)

    text = models.TextField(blank= True, null= True)

    created_at = models.DateTimeField(auto_now_add = True)

    voyage = models.ForeignKey(Voyage,related_name= "messages", on_delete= models.CASCADE, blank= True, null= True )

    image = models.ForeignKey(Image, related_name='messages', on_delete=models.CASCADE, null=True, blank=True)

    audio = models.ForeignKey(Audio, related_name="messages", on_delete=models.CASCADE, null=True, blank=True)
    
    typ = models.CharField(max_length=10, default="norm")
    
    def get_image(self) :
        return self.image.url() if self.image else None
    
    def get_audio(self) :
        return self.audio.url() if self.audio else None
    

class Notification(models.Model):

    message = models.TextField()

    canals = models.CharField(max_length= 50, default= "whatsapp")

    receiver = models.ForeignKey(Voyage,related_name= "notification",on_delete= models.CASCADE, blank= True, null= True )

    types = models.CharField(max_length= 50,blank= True, null= True)

class Portefeuille(models.Model) :
    user = models.ForeignKey(User, related_name="portefeuille", null=True, blank=True, on_delete=models.SET_NULL)
    
    def get_amount(self) :
        tot = 0
        for t in self.transactions.all() :
            tot += t.amount
        
        return tot
    def can_pay(self, price ) :
        return self.get_amount() >= price

class Transaction(models.Model) :
    portefeuille = models.ForeignKey(Portefeuille, on_delete=models.CASCADE, related_name="transactions")
    created_at = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField(default=0)
    typ = models.CharField(max_length=50, default='En attente')
    transaction_id = models.CharField(max_length=150, null=True, blank=True)
    

    