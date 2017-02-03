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

    transaction_by_categories = request.user.transactions \
        .filter(transaction_date__year=timezone.now().date().year) \
        .values('category__name')\
        .annotate(income=Sum('credit'), expense=Sum('debit'))\
        .order_by('category__name')

    transactions = request.user.transactions\
        .filter(transaction_date__year=timezone.now().date().year)\
        .annotate(month=TruncMonth('transaction_date'))\
        .values('month')\
        .annotate(income=Sum('credit'), expense=Sum('debit'))\
        .order_by('month')

    months = ['Jan', 'Feb', 'Mar', 'Apr', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    transaction_months = [transaction['month'].strftime("%b") for transaction in transactions]
    barchar_income_series = [float(transaction['income']) for transaction in transactions]
    barchar_expense_series = [float(transaction['expense']) for transaction in transactions]

    for month in months:
        if not month in transaction_months:
            transaction_months += [month]
            barchar_income_series += [float(0)]
            barchar_expense_series += [float(0)]

    bar_chart_series = [
        {
            'name': 'Income',
            'data': barchar_income_series
        },
        {
            'name': 'Expense',
            'data': barchar_expense_series
        }
    ]

    pie_chart_expense_series = [[transaction['category__name'], float(transaction['expense'])] for transaction in transaction_by_categories]
    pie_chart_income_series = [[transaction['category__name'], float(transaction['income'])] for transaction in transaction_by_categories]

    context = {
        'categories': categories,
        'transactions': transactions,
        'bar_chart_categories': json.dumps(transaction_months),
        'bar_chart_series': json.dumps(bar_chart_series),
        'pie_chart_expense_series': json.dumps(pie_chart_expense_series),
        'pie_chart_income_series': json.dumps(pie_chart_income_series)
    }

    return render(request, 'pages/dashboard.html', context)
