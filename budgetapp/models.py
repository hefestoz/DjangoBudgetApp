from django.db import models

class Transaction(models.Model):
    TYPE_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    user = models.CharField(max_length=100)
    date = models.DateField(auto_now_add=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    amount = models.IntegerField()  
    description = models.TextField(blank=True)

    
    def totaltransaction(self):
        if self.type == 'income':
            return self.amount
        else:
            return -self.amount
    
       
    def total_balance_for_user(self):
        incomes = Transaction.objects.filter(user=self.user, type='income').aggregate(total=models.Sum('amount')) or 0
        expenses = Transaction.objects.filter(user=self.user, type='expense').aggregate(total=models.Sum('amount')) or 0

        return incomes['total'] - expenses['total']
    
    @classmethod
    def total_balance(self):
        total_income = Transaction.objects.filter(type='income').aggregate(total=models.Sum('amount'))['total'] or 0
        total_expense = Transaction.objects.filter(type='expense').aggregate(total=models.Sum('amount'))['total'] or 0
        balance = total_income - total_expense
        return balance
    
    @classmethod
    def total_income(self):
        return Transaction.objects.filter(type='income').aggregate(total=models.Sum('amount'))['total'] or 0
    
    @classmethod
    def total_expense(self):
        return Transaction.objects.filter(type='expense').aggregate(total=models.Sum('amount'))['total'] or 0
    
    @classmethod
    def __str__(self):
        return f"{self.user} - {self.type.capitalize()} - {self.date} - {self.amount}"


