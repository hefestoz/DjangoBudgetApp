from django.test import TestCase

from .models import Transaction

t1 = Transaction(user='Chris', type='income', amount=2000, description='testing the test')
t2 = Transaction(user='Chris', type='expense', amount=1000, description='Retesting the test')
t3 = Transaction(user='Chris', type='income', amount=4000, description='Retesting the test')
t1.save()
t2.save()

Transaction.objects.all()
balance = Transaction.total()
print(balance)

tx = Transaction.objects.filter(user='Chris').first()
balance = tx.__str__()
print(balance)
