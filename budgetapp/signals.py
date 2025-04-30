# budgetapp/signals.py
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Category, Subcategory

@receiver(post_migrate)
def create_default_categories(sender, **kwargs):
    if sender.name != "budgetapp":
        return

    categories = {
        'Housing': [
            'rent',
            'Water',
            'Natural gas',
            'Electricity',
            'Cable/internet'
        ],
        'paycheck': ['Salary', 'Income'],
        'Food': ['Groceries', 'Restaurants'],
        'Transportation': ['Gas', 'Maintenance', 'Transport Bus'],
        'Personal': ['Clothing', 'Phone', 'Fun money', 'Hair/cosmetics', 'Subscriptions'],
        'Lifestyle': ['Pet Care', 'Childcare', 'Entertainment', 'Miscellaneous'],
        'Insurance': ['Health', 'Life', 'Auto', 'Theft']
    }

    for cat_name, subcat_list in categories.items():
        category, _ = Category.objects.get_or_create(name=cat_name)
        for subcat_name in subcat_list:
            Subcategory.objects.get_or_create(name=subcat_name, category=category)
