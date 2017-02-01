from datetime import date

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone

from transactions.filters import TransactionFilter
from transactions.utils import export_to_xlsx
from .forms import ExpenseForm, IncomeForm
from .models import Transaction


@login_required
def transaction_list(request):
    """
    List all transactions
    """
    today = timezone.now().date()

    per_page = settings.PAGE_SIZE
    page = request.GET.get('page', 1)
    search = request.GET.get('search', '')
    from_date = request.GET.get('from_date', str(today - timezone.timedelta(days=30)))
    to_date = request.GET.get('to_date', str(today))

    filter_args = {
        'page': page,
        'search': search,
        'from_date': from_date,
        'to_date': to_date,
    }
    f = TransactionFilter(filter_args, queryset=request.user.transactions.all())
    transactions = f.qs

    if request.GET.get('excel'):
        return export_to_xlsx(transactions, from_date, to_date)

    total_income = 0.0
    total_expense = 0.0
    current_month = date(today.year, today.month, 1)
    current_month_transactions = request.user.transactions.filter(transaction_date__gte=current_month)

    for transaction in current_month_transactions:
        if transaction.type == 'Income':
            total_income += float(transaction.credit)
        elif transaction.type == 'Expense':
            total_expense += float(transaction.debit)

    paginator = Paginator(transactions, per_page)
    try:
        transactions = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        transactions = paginator.page(page)
    except EmptyPage:
        page = 1
        transactions = paginator.page(paginator.num_pages)

    sn = per_page * (int(page) - 1)
    context = {
        'search': search,
        'from_date': from_date,
        'to_date': to_date,
        'sn': sn,
        'transactions': transactions,
        'total_income': total_income,
        'total_expense': total_expense,
        'balance_left': total_income - total_expense,
    }
    return render(request, 'transactions/list.html', context)


@login_required
def expense_create(request):
    """
    Create an expense
    """
    initial_data = {
        'transaction_date': timezone.now().date(),
    }
    form = ExpenseForm(data=request.POST or None, user=request.user, initial=initial_data)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Expense added.")
            return redirect("transactions:expense_create")

    context = {
        'form': form
    }
    return render(request, 'transactions/expense_create.html', context)


@login_required
def income_create(request):
    """
    Create an income
    """
    initial_data = {
        'transaction_date': timezone.now().date,
    }
    form = IncomeForm(data=request.POST or None, user=request.user, initial=initial_data)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Income added.")
            return redirect("transactions:income_create")

    context = {
        'form': form
    }
    return render(request, 'transactions/income_create.html', context)


@login_required
def transaction_edit(request, pk):
    """
    Edit transaction
    """
    try:
        transaction = request.user.transactions.get(pk=pk)
    except Transaction.DoesNotExist:
        raise Http404()

    if transaction.type == 'Expense':
        form = ExpenseForm(instance=transaction, data=request.POST or None, user=request.user)
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                messages.success(request, "Expense updated.")
                return redirect(reverse('transactions:edit', kwargs={'pk': pk}))

        context = {
            'form': form
        }
        return render(request, 'transactions/expense_edit.html', context)
    else:
        form = IncomeForm(instance=transaction, data=request.POST or None, user=request.user)
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                messages.success(request, "Income updated.")
                return redirect(reverse('transactions:edit', kwargs={'pk': pk}))

        context = {
            'form': form
        }
        return render(request, 'transactions/income_edit.html', context)


@login_required
def transaction_delete(request, pk):
    """
    Delete a transaction
    """
    try:
        transaction = request.user.transactions.get(pk=pk)
    except Transaction.DoesNotExist:
        raise Http404()

    if request.method == 'POST':
        transaction.delete()
        messages.success(request, "Transaction %s deleted." % transaction.title)
        return redirect('transactions:list')

    context = {
        'transaction': transaction
    }
    return render(request, 'transactions/delete.html', context)
