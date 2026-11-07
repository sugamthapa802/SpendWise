from datetime import date
from decimal import Decimal
from django.db.models import Sum

def _next_month(first_of_month: date):
    if first_of_month.month == 12:
        return date(first_of_month.year + 1 , 1,1)
    return date(first_of_month.year,first_of_month.month + 1, 1)

def budget_usage(budget_category):
    from .models import Transaction
    month_start = budget_category.month
    month_end = _next_month(month_start)
    spent = (
        Transaction.objects.filter(
            user = budget_category.user,
            category = budget_category,
            date_gte = month_start, 
            date_lt = month_end, 
        ). aggregate(total = Sum("amount"))["total"]
        or Decimal("0")
        )
    remaining = budget_category.amount - spent
    spent_percentage = (spent / budget_category.amount) * 100 if budget_category.amount else Decimal("0")
    return spent, remaining, spent_percentage
