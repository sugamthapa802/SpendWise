from django.shortcuts import render
from .serializers import UserSerializer,RegisterSerializer,CategorySerializer
from django.contrib.auth import get_user_model
from rest_framework.generics import CreateAPIView,ListAPIView,RetrieveAPIView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Category

User= get_user_model()

class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer


class MeView(RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user



class CategoryViewset(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def  get_queryset(self):
        return Category.objects.filter(user=self.request.user)
