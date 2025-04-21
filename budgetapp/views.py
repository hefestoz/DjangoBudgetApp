from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Transaction
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .serializers import TransactionSerializer

def index(request):

    if request.method == 'POST':
        # take data from form
        user = request.POST.get('user')
        type = request.POST.get('type')
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        
        #create transaction in database
        Transaction.objects.create(user=user, type=type, amount=amount, description=description)

        return redirect('index')
     
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
    return render(request, 'budgetapp/index.html', context)


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

@api_view(['GET'])
def transaction_totals(request):
    balance = Transaction.total_balance()
    total_income = Transaction.total_income()
    total_expense = Transaction.total_expense()
    return Response({'balance': balance, 
                     'total_income': total_income,
                     'total_expense': total_expense}) 


