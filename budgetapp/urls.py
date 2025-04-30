from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="main"),
    path("transactions/", views.transactions_info, name="transactions"),
    path("api/transactions/", views.transaction_list, name="transaction_list"),
    path('api/users/', views.user_list, name='user_list'),
    path('accounts/profile/', views.user_profile, name='account_profile'),
    path('export/csv/', views.export_transactions_csv, name='export_transactions_csv'),
    path('export/pdf/', views.export_transactions_pdf, name='export_transactions_pdf'),
    path('transactions/new/', views.add_transaction, name='add-transaction'),
    path('api/subcategories/', views.get_subcategories, name='get-subcategories'),
    path('summary/', views.financial_summary, name='financial-summary'),
    ]
