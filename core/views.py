from django.shortcuts import render
from .serializers import UserSerializer,RegisterSerializer,CategorySerializer, TransactionSerializer, BudgetSerializer, CashFlowSummarySerializer, SummaryQuerySerializer
from django.contrib.auth import get_user_model
from rest_framework.generics import CreateAPIView,RetrieveAPIView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter,OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category,Transaction, Budget
from .tasks import check_budget_threshold
from django.db.models import Sum, Count, Q, DecimalField, Value
from django.db.models.functions import Coalesce
from rest_framework.response import Response
from rest_framework.views import APIView


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
    
class BudgetViewset(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["month", "category", "amount"]
    ordering_fields = ["created_at", "amount"]

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)


class SummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        q = SummaryQuerySerializer(data=request.query_params)
        q.is_valid(raise_exception=True)
        start = q.validated_data["start"]
        end   = q.validated_data["end"]

        totals = Transaction.objects.filter(
            user=request.user,
            date__gte=start,
            date__lte=end,
        ).aggregate(
            income=Coalesce(
                Sum("amount", filter=Q(category__type=Category.CategoryType.INCOME)),
                Value(0),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            ),
            expense=Coalesce(
                Sum("amount", filter=Q(category__type=Category.CategoryType.EXPENSE)),
                Value(0),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            ),
            count=Count("id"),
        )

        payload = {
            "period_start": start,
            "period_end": end,
            "income": totals["income"],
            "expense": totals["expense"],
            "net": totals["income"] - totals["expense"],
            "transaction_count": totals["count"],
        }
        return Response(CashFlowSummarySerializer(payload).data)
