from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("api/transactions/", views.transaction_list, name="transaction_list"),
    path("api/totals/", views.transaction_totals, name="transaction_totals"),
    ]