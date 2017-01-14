from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone

from .forms import ExpenseForm, IncomeForm
from .models import Transaction


@login_required
def transaction_list(request):
    """
    List all transactions
    """
    page = request.GET.get('page', 1)
    per_page = settings.PAGE_SIZE
    transactions = request.user.transactions.all()
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
        'sn': sn,
        'transactions': transactions
    }
    return render(request, 'transactions/list.html', context)


@login_required
def expense_create(request):
    """
    Create an expense
    """
    initial_data = {
        'transaction_date': timezone.now().date,
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
