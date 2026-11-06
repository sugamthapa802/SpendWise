from django.shortcuts import render
from .serializers import UserSerializer,RegisterSerializer,CategorySerializer, TransactionSerializer
from django.contrib.auth import get_user_model
from rest_framework.generics import CreateAPIView,ListAPIView,RetrieveAPIView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter,OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category,Transaction
from .tasks import check_budget_threshold

# User= get_user_model()

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



class TransactionViewset(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields=["category","date"]
    ordering_fields = ["created_at","amount","date"]
    
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        tx=serializer.save(user=self.request.user)
        check_budget_threshold(tx)