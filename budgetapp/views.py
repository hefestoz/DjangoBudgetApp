import io
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, JsonResponse  
from .models import Transaction,Category, Subcategory
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .serializers import TransactionSerializer
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models import Sum
from django.test import RequestFactory
import csv
from fpdf import FPDF, HTMLMixin, HTML2FPDF
from .forms import TransactionForm

def index(request):

    return render(request, 'budgetapp/index.html')

@login_required
def transactions_info(request):

    # code for transactions from web page
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            # take data from form for creation
            amount = request.POST.get('amount')
            description = request.POST.get('description')
            category = request.POST.get('category')
            subcategory_id = request.POST.get('subcategory')

            #create transaction in database
            category = Category.objects.get(pk=category)
            subcategory = Subcategory.objects.get(pk=subcategory_id)
            Transaction.objects.create(
                user=request.user, 
                type=type, 
                amount=amount, 
                description=description,
                category=category,
                subcategory= subcategory,
            )
        
        elif action == 'delete':
            # handle deletion
            delete_id = request.POST.get('delete_id')  # match the form field name
            transaction = Transaction.objects.filter(pk=delete_id, user=request.user).first()
            if transaction:
                transaction.delete()

        return redirect(reverse('transactions'))
    #------------------------------------------------------------------------------
    
    transactions = Transaction.objects.filter(user=request.user).order_by('date')  # Get all transactions sorted by date
    balance = Transaction.total_balance_for_user(request=request)
    total_income = Transaction.total_income(request=request)
    total_expense = Transaction.total_expense(request=request)
    category = Category.objects.all() 
    form = TransactionForm()

    context = {
        'transactions': transactions,
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'categories': category,
        'form': form,
    }
    return render(request, 'budgetapp/transactions.html', context)

def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            return redirect(reverse('transactions'))
    else:
        form = TransactionForm()

    return render(request, 'budgetapp/add_transaction.html', {'form': form})

@login_required
def financial_summary(request):
    user = request.user
    transactions = Transaction.objects.filter(user=user)
    balance = Transaction.total_balance_for_user(request=request)
    total_income = Transaction.total_income(request=request)
    total_expense = Transaction.total_expense(request=request)

    # Totales por categoría (solo gastos)
    expenses_by_category = (
        transactions
        .filter(type='expense')
        .values('category__name')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )

    categories = [item['category__name'] or "Sin categoría" for item in expenses_by_category]
    totals = [item['total'] for item in expenses_by_category]

    return render(request, 'budgetapp/financial_summary.html', {
        'categories': categories,
        'totals': totals,
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
    })


def export_transactions_csv(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transactions.csv"'

    writer = csv.writer(response)

    writer.writerow(['Date', 'Type', 'Amount', 'Description', 'Category', 'Subcategory'])

    for transaction in transactions:
        writer.writerow([
            transaction.date,
            transaction.type, 
            transaction.amount, 
            transaction.description,
            transaction.category.name if transaction.category else '-',
            transaction.subcategory.name if transaction.subcategory else '-',
        ])  
    return response


class HTML2PDF(HTMLMixin, FPDF):
    pass

def export_transactions_pdf(request):
    from datetime import datetime
    transactions = Transaction.objects.filter(user=request.user)
    
    # Calculate totals
    total_income = sum(t.amount for t in transactions if t.type == 'income')
    total_expense = sum(t.amount for t in transactions if t.type == 'expense')
    balance = total_income - total_expense

    # Create PDF
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font('Arial', '', 12)

    # Header
    pdf.set_font('Arial', 'B', 18)
    pdf.cell(0, 10, 'BudgetProyect', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 6, f'User: {request.user.get_username()}', 0, 1)
    pdf.cell(0, 6, f'Date: {datetime.now().strftime("%Y-%m-%d")}', 0, 1)
    pdf.ln(10)  # Add some space

    # Summary section
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Financial Summary', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 6, f'Total Income: ${total_income}', 0, 1)
    pdf.cell(0, 6, f'Total Expense: ${total_expense}', 0, 1)
    pdf.cell(0, 6, f'Balance: ${balance}', 0, 1)
    pdf.ln(10)  # Add some space

    # Transactions table header
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Transaction Details', 0, 1)
    
    # Table column widths
    col_widths = [40, 40, 40, 70]  # Adjust as needed
    
    # Table header
    pdf.set_font('Arial', 'B', 12)
    pdf.set_fill_color(240, 240, 240)  # Light gray background
    pdf.cell(col_widths[0], 10, 'Date', 1, 0, 'L', 1)
    pdf.cell(col_widths[1], 10, 'Type', 1, 0, 'L', 1)
    pdf.cell(col_widths[2], 10, 'Amount', 1, 0, 'L', 1)
    pdf.cell(col_widths[3], 10, 'Description', 1, 1, 'L', 1)
    
    # Table rows
    pdf.set_font('Arial', '', 12)
    pdf.set_fill_color(255, 255, 255)  # White background
    for t in transactions:
        # Check if we need a new page
        if pdf.get_y() > 250:  # Near bottom of page
            pdf.add_page()
            # Reprint table header on new page
            pdf.set_font('Arial', 'B', 12)
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(col_widths[0], 10, 'Date', 1, 0, 'L', 1)
            pdf.cell(col_widths[1], 10, 'Type', 1, 0, 'L', 1)
            pdf.cell(col_widths[2], 10, 'Amount', 1, 0, 'L', 1)
            pdf.cell(col_widths[3], 10, 'Description', 1, 1, 'L', 1)
            pdf.set_font('Arial', '', 12)
            pdf.set_fill_color(255, 255, 255)
        
        pdf.cell(col_widths[0], 10, t.date.strftime('%Y-%m-%d'), 1, 0, 'L', 1)
        pdf.cell(col_widths[1], 10, t.get_type_display(), 1, 0, 'L', 1)
        pdf.cell(col_widths[2], 10, f'${t.amount}', 1, 0, 'L', 1)
        pdf.cell(col_widths[3], 10, t.description or '-', 1, 1, 'L', 1)

    # generate pdf to buffer
    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf', headers={
        'Content-Disposition': 'attachment; filename="transactions.pdf"',
    })
    return response


#API endpoint for transactions "api/transactions/"
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


#API endpoint for users includes financial summary
@api_view(['GET'])
def user_list(request):

    users = User.objects.all()

    user_data = []

    for user in users:
         # mock request created to get the user's financial summary, this help to avoid circular import
        
        mock_request = RequestFactory().get('/')
        mock_request.user = user
        transactions = Transaction.objects.filter(user=user)  
    
        user_data.append({
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "date_joined": user.date_joined,
            "financial_summary": {
                "balance": Transaction.total_balance_for_user(mock_request),
                "total_income": Transaction.total_income(mock_request),
                "total_expense": Transaction.total_expense(mock_request),
                "transactions_count": transactions.count()
            },
            "transaction_list": [
                {
                    "date": transaction.date.strftime('%Y-%m-%d'),
                    "type": transaction.get_type_display(),
                    "amount": f"${transaction.amount}",
                    "description": transaction.description or '-',
                    "category": transaction.category.name if transaction.category else '-',
                    "subcategory": transaction.subcategory.name if transaction.subcategory else '-',
                }
                for transaction in transactions
            ]
        })

@api_view(['GET'])
def user_detail(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

    transactions = Transaction.objects.filter(user=user)

    mock_request = RequestFactory().get('/')
    mock_request.user = user

    transaction_list = [
        {
            "date": t.date.strftime('%Y-%m-%d'),
            "type": t.get_type_display(),
            "amount": f'${t.amount}',
            "description": t.description or '-',
            "category": t.category.name if t.category else '-',
            "subcategory": t.subcategory.name if t.subcategory else '-',
        }
        for t in transactions
    ]

    user_data = {
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "date_joined": user.date_joined,
        "financial_summary": {
            "balance": Transaction.total_balance_for_user(mock_request),
            "total_income": Transaction.total_income(mock_request),
            "total_expense": Transaction.total_expense(mock_request),
            "transactions_count": transactions.count()
        },
        "transaction_list": transaction_list
    }

    return Response(user_data)


def get_subcategories(request):
    category_id = request.GET.get('category')
    subcategories = Subcategory.objects.filter(category_id=category_id).values('id', 'name')
    return JsonResponse(list(subcategories), safe=False)

#view for user profile page after Login
@login_required
def user_profile(request):
    return render(request, 'budgetapp/profile.html', {'user': request.user, 'user.email': request.user.email})