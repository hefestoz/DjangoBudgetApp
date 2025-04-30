from django.db import models
from django.contrib.auth import get_user_model

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Subcategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.category.name} - {self.name}"

class Transaction(models.Model):
    TYPE_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    user = models.CharField(auto_created=True, max_length=100)
    date = models.DateField(auto_now_add=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    amount = models.IntegerField()  
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='transactions', null=True, blank=True)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.SET_NULL, null=True, blank=True)
    
    # automatically set type based on category
    def save(self, *args, **kwargs):
            
            if self.category:
                if self.category.name.lower() == 'paycheck':
                    self.type = 'income'
                else:
                    self.type = 'expense'
            super().save(*args, **kwargs)

    def totaltransaction(self):
        if self.type == 'income':
            return self.amount
        else:
            return -self.amount
    
    def total_balance_for_user(request):
        user = request.user
        incomes = Transaction.objects.filter(user=request.user, type='income').aggregate(total=models.Sum('amount'))['total'] or 0
        expenses = Transaction.objects.filter(user=request.user, type='expense').aggregate(total=models.Sum('amount'))['total'] or 0
        balance = incomes - expenses
        return balance

    def total_income(request):
        incomes = Transaction.objects.filter(user=request.user, type='income').aggregate(total=models.Sum('amount'))['total'] or 0
        return incomes
    
    def total_expense(request):
        expenses = Transaction.objects.filter(user=request.user, type='expense').aggregate(total=models.Sum('amount'))['total'] or 0
        return expenses
    
    @classmethod
    def __str__(self):
        return f"{self.user} - {self.type.capitalize()} - {self.date} - {self.amount}"


