from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    username=None
    ROLE_CHOICES = [
        ('EDITOR','Editor'),
        ('SUBSCRIBER','Subscriber')
    ]
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    role = models.CharField(max_length=15,choices=ROLE_CHOICES,default='SUBSCRIBER')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    def __str__(self):
        return f"{self.email} - {self.role}"
    
class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='profile')
    bio = models.CharField(max_length=150,blank=True,null=True)
    address = models.CharField(max_length=200,blank=True,null=True)
    image = models.ImageField(upload_to='profiles/',blank=True,null=True)

    def __str__(self):
        return self.user.first_name