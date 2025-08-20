from djoser.serializers import UserCreateSerializer as BaseUserCreateSerialzier,UserSerializer as BaseUserSerializer


class UserCreateSerializer(BaseUserCreateSerialzier):
    class Meta(BaseUserCreateSerialzier.Meta):
        fields =['id','first_name','last_name','email','phone_number','password']


class CurrentUserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields =['id','first_name','last_name','email','phone_number']