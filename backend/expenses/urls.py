from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, RegisterView, TransactionViewSet, monthly_trend, summary

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("transactions", TransactionViewSet, basename="transaction")

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("reports/summary/", summary, name="summary"),
    path("reports/monthly/", monthly_trend, name="monthly-trend"),
    path("", include(router.urls)),
]
