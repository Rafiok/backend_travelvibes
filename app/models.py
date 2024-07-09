from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
import os

ENDPOINT = os.environ.get('ENDOINT', 'http://localhost:8080')

# Create your models here.

class OurDetails(models.Model) :
    key = models.CharField(max_length=150)
    value = models.TextField()

def g_v(key : str) :
    return OurDetails.objects.get(key = key)


class CustomUserManager(BaseUserManager): 
    def create_user(self, email, password, **extra_fields):
        """ if not (email ):
            raise ValueError("l'email ou le numéro ne peuvent etre nulls") """
        
        user = self.model(email = email,  **extra_fields)    
        user.set_password(password)
        user.save()
        return user
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_superuser',True)
        extra_fields.setdefault('is_active',True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError("Le Super utilisateur doit forcément avoir la variable is_staf à True")
        
        if extra_fields.get('is_superuser') is not True:

            raise ValueError("Le Super utilisateur doit forcément avoir la variable is_superuser à True")
        return self.create_user( email, password, **extra_fields)

class Image(models.Model) :
    name = models.CharField(default='profil', max_length=500)
    file = models.ImageField(upload_to="images/")

    def __str__(self) -> str:
        return self.name
    
    def url(self) :
        return ENDPOINT + self.file.url
    
class Audio(models.Model) :
    name = models.CharField(default='profil', max_length=500)
    file = models.ImageField(upload_to="audio/")

    def __str__(self) -> str:
        return self.name
    
    def url(self) :
        return ENDPOINT + self.file.url

class User(AbstractBaseUser,PermissionsMixin):
    nom = models.CharField(max_length= 150, blank= True, null= True)
    number = models.CharField(max_length= 150, )
    sex= models.CharField(max_length=50, null=True, blank=True)
    whatsapp = models.CharField(max_length= 150, blank= True, null= True)
    email = models.EmailField(unique=True) 
    is_staff = models.BooleanField(default= False)
    is_active = models.BooleanField(default= True)
    objects = CustomUserManager() 
    created_at = models.DateTimeField(auto_now_add = True)
    username = models.CharField(max_length=150)
    profil = models.ForeignKey(Image, related_name="users", on_delete=models.SET_NULL, null=True, blank=True)
    REQUIRED_FIELDS = []
    USERNAME_FIELD = "username"

    def get_profil(self) :
        return self.profil.url() if self.profil else g_v('profil:default')

    def __str__(self) -> str:
        return f"{self.prenom} {self.nom}"





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






class Voyage(models.Model):
    voyageur = models.ForeignKey(User, on_delete= models.CASCADE, related_name= "voyages", blank= True, null= True) 

    lieux_depart = models.ForeignKey(Lieu, on_delete= models.SET_NULL, related_name= "voyages_depart", blank= True, null= True)

    lieux_arrive = models.ForeignKey(Lieu, on_delete= models.SET_NULL, related_name= "voyages_arrives", blank= True, null= True)

    date_depart = models.DateTimeField(blank= True, null= True)
    
    state = models.CharField(max_length= 50, default= "en attente")

    voyage_correspondant = models.OneToOneField(VoyagePrevu, models.SET_NULL, blank= True, null= True)


class Message(models.Model):

    user = models.ForeignKey(User, related_name= "messages",on_delete= models.CASCADE,blank= True, null= True)

    text = models.TextField(blank= True, null= True)

    created_at = models.DateTimeField(auto_now_add = True)

    voyage = models.ForeignKey(Voyage,related_name= "messages", on_delete= models.CASCADE, blank= True, null= True )



class Notification(models.Model):

    message = models.TextField()

    canals = models.CharField(max_length= 50, default= "whatsapp")

    receiver = models.ForeignKey(Voyage,related_name= "notification",on_delete= models.CASCADE, blank= True, null= True )

    types = models.CharField(max_length= 50,blank= True, null= True)






