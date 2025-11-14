from djoser.serializers import UserCreateSerializer as BaseUserCreateSerialzier,UserSerializer as BaseUserSerializer
from rest_framework import serializers
from users.models import UserProfile,User,SubscriptionPlan
class UserCreateSerializer(BaseUserCreateSerialzier):
    class Meta(BaseUserCreateSerialzier.Meta):
        fields =['id','first_name','last_name','email','phone_number','password']


class CurrentUserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields =['id','first_name','last_name','email','phone_number','role']
        read_only_fields=['role']


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields=['user','bio','address','image']


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields =['id','first_name','last_name','email','phone_number','role','is_active']


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    class Meta:
        model = SubscriptionPlan
        fields =['id','name','price','features','price_cents']
    def get_price(self,obj):
        return obj.price_cents / 130.0 if obj.price_cents else 0.0
    