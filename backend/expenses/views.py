from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models import Q, Sum
from django.db.models.functions import TruncMonth
from rest_framework import generics, permissions, serializers, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .filters import TransactionFilter
from .models import Category, Transaction
from .serializers import CategorySerializer, RegisterSerializer, TransactionSerializer

User = get_user_model()
ZERO = Decimal("0.00")


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    pagination_class = None
    filterset_fields = ("kind",)

    def get_queryset(self):
        return Category.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def destroy(self, request, *args, **kwargs):
        category = self.get_object()
        if category.transactions.exists():
            return Response(
                {"detail": "This category has transactions and cannot be deleted."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    filterset_class = TransactionFilter
    search_fields = ("description", "category__name")
    ordering_fields = ("date", "amount", "created_at")

    def get_queryset(self):
        return Transaction.objects.filter(owner=self.request.user).select_related("category")

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


def _parse_month(value):
    """Parse 'YYYY-MM' into the first day of that month (defaults to today)."""
    if not value:
        today = date.today()
        return date(today.year, today.month, 1)
    try:
        year, month = (int(part) for part in value.split("-"))
        return date(year, month, 1)
    except (ValueError, TypeError):
        raise serializers.ValidationError({"month": "Use the format YYYY-MM."})


def _next_month(day):
    return date(day.year + (day.month == 12), day.month % 12 + 1, 1)


@api_view(["GET"])
def summary(request):
    """Totals for a month: income, expenses, balance and spending by category."""
    start = _parse_month(request.query_params.get("month"))
    end = _next_month(start)
    qs = Transaction.objects.filter(owner=request.user, date__gte=start, date__lt=end)

    totals = qs.aggregate(
        income=Sum("amount", filter=Q(category__kind=Category.Kind.INCOME)),
        expenses=Sum("amount", filter=Q(category__kind=Category.Kind.EXPENSE)),
    )
    income = totals["income"] or ZERO
    expenses = totals["expenses"] or ZERO

    by_category = (
        qs.filter(category__kind=Category.Kind.EXPENSE)
        .values("category__name", "category__color")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )

    return Response(
        {
            "month": start.strftime("%Y-%m"),
            "income": income,
            "expenses": expenses,
            "balance": income - expenses,
            "by_category": [
                {"category": row["category__name"], "color": row["category__color"], "total": row["total"]}
                for row in by_category
            ],
        }
    )


@api_view(["GET"])
def monthly_trend(request):
    """Income vs expenses per month for the last N months (default 6, max 24)."""
    try:
        months = min(max(int(request.query_params.get("months", 6)), 1), 24)
    except ValueError:
        months = 6

    end = _next_month(_parse_month(None))
    start = end
    for _ in range(months):
        start = date(start.year - (start.month == 1), (start.month - 2) % 12 + 1, 1)

    rows = (
        Transaction.objects.filter(owner=request.user, date__gte=start, date__lt=end)
        .annotate(month=TruncMonth("date"))
        .values("month")
        .annotate(
            income=Sum("amount", filter=Q(category__kind=Category.Kind.INCOME)),
            expenses=Sum("amount", filter=Q(category__kind=Category.Kind.EXPENSE)),
        )
        .order_by("month")
    )
    by_month = {row["month"].strftime("%Y-%m"): row for row in rows}

    data, current = [], start
    while current < end:
        key = current.strftime("%Y-%m")
        row = by_month.get(key, {})
        data.append(
            {
                "month": key,
                "income": row.get("income") or ZERO,
                "expenses": row.get("expenses") or ZERO,
            }
        )
        current = _next_month(current)
    return Response(data)
