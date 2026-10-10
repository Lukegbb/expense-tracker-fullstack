from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from expenses.models import Category, Transaction

User = get_user_model()


class AuthTests(APITestCase):
    def test_register_creates_default_categories(self):
        response = self.client.post(
            reverse("register"),
            {"username": "lucas", "email": "lucas@example.com", "password": "Str0ng-pass-123"},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username="lucas")
        self.assertEqual(user.categories.count(), 5)

    def test_endpoints_require_authentication(self):
        self.assertEqual(
            self.client.get(reverse("transaction-list")).status_code,
            status.HTTP_401_UNAUTHORIZED,
        )


class ExpenseApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("alice", password="Str0ng-pass-123")
        self.other = User.objects.create_user("bob", password="Str0ng-pass-123")
        self.client.force_authenticate(self.user)

        self.salary = Category.objects.create(owner=self.user, name="Salary", kind="income")
        self.food = Category.objects.create(owner=self.user, name="Food", kind="expense", color="#f59e0b")
        self.rent = Category.objects.create(owner=self.user, name="Rent", kind="expense", color="#dc2626")

    def add(self, category, amount, day):
        return Transaction.objects.create(
            owner=self.user, category=category, amount=Decimal(amount), date=day
        )

    def test_create_transaction(self):
        response = self.client.post(
            reverse("transaction-list"),
            {"category": self.food.id, "amount": "25.50", "date": "2026-10-01", "description": "Lunch"},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["kind"], "expense")
        self.assertEqual(response.data["category_name"], "Food")

    def test_amount_must_be_positive(self):
        response = self.client.post(
            reverse("transaction-list"),
            {"category": self.food.id, "amount": "0", "date": "2026-10-01"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_use_other_users_category(self):
        foreign = Category.objects.create(owner=self.other, name="Food", kind="expense")
        response = self.client.post(
            reverse("transaction-list"),
            {"category": foreign.id, "amount": "10.00", "date": "2026-10-01"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_only_sees_own_transactions(self):
        self.add(self.food, "10.00", date(2026, 10, 1))
        other_cat = Category.objects.create(owner=self.other, name="Food", kind="expense")
        Transaction.objects.create(
            owner=self.other, category=other_cat, amount=Decimal("99.00"), date=date(2026, 10, 1)
        )
        response = self.client.get(reverse("transaction-list"))
        self.assertEqual(response.data["count"], 1)

    def test_filter_by_kind_and_date_range(self):
        self.add(self.salary, "3000.00", date(2026, 9, 28))
        self.add(self.food, "40.00", date(2026, 10, 2))
        self.add(self.rent, "1200.00", date(2026, 10, 1))

        response = self.client.get(
            reverse("transaction-list"),
            {"kind": "expense", "date_from": "2026-10-01", "date_to": "2026-10-31"},
        )
        self.assertEqual(response.data["count"], 2)

    def test_monthly_summary(self):
        self.add(self.salary, "3000.00", date(2026, 10, 1))
        self.add(self.rent, "1200.00", date(2026, 10, 3))
        self.add(self.food, "50.25", date(2026, 10, 5))
        self.add(self.food, "20.00", date(2026, 9, 30))  # previous month, ignored

        response = self.client.get(reverse("summary"), {"month": "2026-10"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["income"], Decimal("3000.00"))
        self.assertEqual(response.data["expenses"], Decimal("1250.25"))
        self.assertEqual(response.data["balance"], Decimal("1749.75"))
        self.assertEqual(
            [row["category"] for row in response.data["by_category"]], ["Rent", "Food"]
        )

    def test_summary_rejects_invalid_month(self):
        response = self.client.get(reverse("summary"), {"month": "october"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_monthly_trend_returns_requested_months(self):
        response = self.client.get(reverse("monthly-trend"), {"months": 3})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_category_with_transactions_cannot_be_deleted(self):
        self.add(self.food, "10.00", date(2026, 10, 1))
        response = self.client.delete(reverse("category-detail", args=[self.food.id]))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        empty = Category.objects.create(owner=self.user, name="Gym", kind="expense")
        response = self.client.delete(reverse("category-detail", args=[empty.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
