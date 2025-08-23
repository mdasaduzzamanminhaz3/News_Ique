from djoser.serializers import UserCreateSerializer as BaseUserCreateSerialzier,UserSerializer as BaseUserSerializer
from rest_framework import serializers
from users.models import UserProfile
class UserCreateSerializer(BaseUserCreateSerialzier):
    class Meta(BaseUserCreateSerialzier.Meta):
        fields =['id','first_name','last_name','email','phone_number','password']


class CurrentUserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields =['id','first_name','last_name','email','phone_number']


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields=['user','bio','address','image']