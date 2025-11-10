from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from users.serializers import UserListSerializer
from users.models import User
from rest_framework.permissions import IsAdminUser
# Create your views here.


class UserListView (ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes =[IsAdminUser]