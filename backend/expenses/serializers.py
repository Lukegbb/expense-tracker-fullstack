import re

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Category, Transaction

User = get_user_model()

DEFAULT_CATEGORIES = [
    ("Salary", Category.Kind.INCOME, "#16a34a"),
    ("Rent", Category.Kind.EXPENSE, "#dc2626"),
    ("Groceries", Category.Kind.EXPENSE, "#f59e0b"),
    ("Transport", Category.Kind.EXPENSE, "#2563eb"),
    ("Leisure", Category.Kind.EXPENSE, "#9333ea"),
]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ("id", "username", "email", "password")

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        # Give every new user a useful starting set of categories.
        Category.objects.bulk_create(
            Category(owner=user, name=name, kind=kind, color=color)
            for name, kind, color in DEFAULT_CATEGORIES
        )
        return user


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "kind", "color")

    def validate_color(self, value):
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
            raise serializers.ValidationError("Use a hex colour such as #2563eb.")
        return value

    def validate_name(self, name):
        user = self.context["request"].user
        qs = Category.objects.filter(owner=user, name__iexact=name)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("You already have a category with this name.")
        return name


class TransactionSerializer(serializers.ModelSerializer):
    kind = serializers.CharField(source="category.kind", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Transaction
        fields = (
            "id",
            "category",
            "category_name",
            "kind",
            "amount",
            "date",
            "description",
            "created_at",
        )
        read_only_fields = ("created_at",)

    def validate_category(self, category):
        if category.owner != self.context["request"].user:
            raise serializers.ValidationError("Category not found.")
        return category
