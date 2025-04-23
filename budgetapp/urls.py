from django.urls import path
from .views import user_profile
from . import views

urlpatterns = [
    path("", views.index, name="main"),
    path("transactions/", views.transactions_info, name="transactions"),
    path("api/transactions/", views.transaction_list, name="transaction_list"),
    path("api/totals/", views.transaction_totals, name="transaction_totals"),
    path('api/users/', views.user_list, name='user_list'),
    path('accounts/profile/', user_profile, name='account_profile'),
    ]
