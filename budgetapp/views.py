from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Transaction
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .serializers import TransactionSerializer
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


def index(request):

    return render(request, 'budgetapp/index.html')

def transactions_info(request):

    if request.method == 'POST':
        # take data from form
        user = request.POST.get('user')
        type = request.POST.get('type')
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        
        #create transaction in database
        Transaction.objects.create(user=user, type=type, amount=amount, description=description)

        return redirect('transactions/')
     
    transactions = Transaction.objects.all().order_by('-date')  # Get all transactions sorted by date
    balance = Transaction.total_balance()
    total_income = Transaction.total_income()
    total_expense = Transaction.total_expense()

    context = {
        'transactions': transactions,
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
    }
    return render(request, 'budgetapp/transactions.html', context)

#API endpoint for totals "api/transactions/"
@api_view(['GET', 'POST' , 'DELETE'])
def transaction_list(request):
    if request.method == 'GET':
        transactions = Transaction.objects.all()
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED) #created
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) #bad request
    
    elif request.method == 'DELETE':
        transaction = Transaction.objects.get(pk=request.data['id'])
        transaction.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

#API endpoint for totals "api/totals/"
@api_view(['GET'])
def transaction_totals(request):
    balance = Transaction.total_balance()
    total_income = Transaction.total_income()
    total_expense = Transaction.total_expense()
    return Response({'balance': balance, 
                     'total_income': total_income,
                     'total_expense': total_expense}) 

#API endpoint for users "api/users/"
@api_view(['GET'])
def user_list(request):
    users = User.objects.all()
    user_data = []

    for user in users:
        user_data.append({
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "date_joined": user.date_joined,
            })  

    return Response(user_data)

#view for user profile page after Login
@login_required
def user_profile(request):
    return render(request, 'budgetapp/profile.html', {'user': request.user, 'user.email': request.user.email})