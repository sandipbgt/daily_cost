import json

from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import render, redirect


def home(request):
    """
    Home page
    """
    if request.user.is_authenticated():
        return redirect('dashboard')
    context = {}
    return render(request, 'pages/home.html', context)


@login_required
def dashboard(request):
    """
    User dashboard page
    """
    categories = request.user.categories.all()

    transactions = request.user.transactions\
        .filter(transaction_date__year=timezone.now().date().year)\
        .annotate(month=TruncMonth('transaction_date'))\
        .values('month')\
        .annotate(income=Sum('credit'), expense=Sum('debit'))\
        .order_by('month')

    bar_chart_series = [
        {
            'name': 'Income',
            'data': [float(transaction['income']) for transaction in transactions]
        },
        {
            'name': 'Expense',
            'data': [float(transaction['expense']) for transaction in transactions]
        }
    ]

    context = {
        'categories': categories,
        'transactions': transactions,
        'bar_chart_categories': json.dumps([transaction['month'].strftime("%b") for transaction in transactions]),
        'bar_chart_series': json.dumps(bar_chart_series),
    }

    return render(request, 'pages/dashboard.html', context)
