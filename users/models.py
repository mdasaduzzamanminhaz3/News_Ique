from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    ROLE_CHOICES = [
        ('EDITOR','Editor'),
        ('SUBSCRIBER','Subscriber')
    ]

    address = models.CharField(max_length=200,blank=True,null=True)
    phone_number = models.CharField(max_length=15)
    role = models.CharField(max_length=15,choices=ROLE_CHOICES,default='SUBSCRIBER')

    def __str__(self):
        return self.username