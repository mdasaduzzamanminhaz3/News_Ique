from rest_framework import serializers
from users.models import User,UserProfile

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields =['id','email','first_name','last_name','password','role']

    def create(self, validated_data):
        user =User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name = validated_data.get('first_name',""),
            last_name = validated_data.get('last_name',""),
            role=validated_data.get('role','SUBSCRIBER')
        )
        return user
    

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id','address','bio','image']