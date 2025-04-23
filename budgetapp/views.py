from django.shortcuts import render, redirect
from django.urls import reverse
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

@login_required
def transactions_info(request):

    # code for transactions from web page
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            # take data from form for creation
            type = request.POST.get('type')
            amount = request.POST.get('amount')
            description = request.POST.get('description')
            # create transaction in database
            Transaction.objects.create(
                user=request.user, 
                type=type, 
                amount=amount, 
                description=description
            )
        
        elif action == 'delete':
            # handle deletion
            delete_id = request.POST.get('delete_id')  # match the form field name
            transaction = Transaction.objects.filter(pk=delete_id, user=request.user).first()
            if transaction:
                transaction.delete()

        return redirect(reverse('transactions'))
    #------------------------------------------------------------------------------
    
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')  # Get all transactions sorted by date
    balance = Transaction.total_balance_for_user(request=request)
    total_income = Transaction.total_income(request=request)
    total_expense = Transaction.total_expense(request=request)

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