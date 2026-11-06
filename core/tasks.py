from decimal import Decimal
from celery import shared_task
from django.conf import settings


def check_budget_threshold(self,transaction_id):
    from .models import Transaction, Notification, Budget
    from .services import budget_usage
    """
    get the transaction obj attached to the transaction_id,
    get the budget related to the transaction,
    calculate the total transaction for that budget and generate notification as per budget usage/limit_left 

    """
    tx = Transaction.objects.filter(id=transaction_id).first()
    if not tx:
        return
    month_start = tx.date.replace(day=1)
    budget = Budget.objects.filter(
        user = tx.user,
        category = tx.category,
        month = month_start
    ).first()
    if not budget:
        return 
    spent, remaining, spent_percentage = budget_usage(budget)
    warning_percent = settings.BUDGET_ALERT_THRESHOLD * 100
    if spent_percentage >= 100:
        Notification.objects.create(
            user_id=tx.user_id,
            budget=budget,
            level=Notification.Level.EXCEEDED,
            message=(
                f"{budget.category.name} budget exceeded: "
                f"{spent}/{budget.limit}"
            ),
        )
    elif spent_percentage >= warning_percent:
        Notification.objects.create(
            user_id=tx.user_id,
            budget=budget,
            level=Notification.Level.WARNING,
            message=(
                f"{budget.category.name} budget at {spent_percentage:.0f}% "
                f"({spent}/{budget.limit})"
            ),
        )