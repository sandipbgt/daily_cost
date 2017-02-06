from calendar import monthrange
from datetime import date

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Sum
from django.http import Http404
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from transactions.filters import TransactionFilter
from transactions.utils import export_to_xlsx, export_to_pdf, get_full_month_names
from .forms import ExpenseForm, IncomeForm
from .models import Transaction


@login_required
def transaction_list(request):
    """
    List all transactions
    """
    today = timezone.now().date()
    action = request.GET.get('action', '')
    output = request.GET.get('output', '')

    if request.is_ajax():
        month = request.GET.get('month')
        if action == 'get_balance_left' and month:
            context = dict()
            data = dict()

            try:
                month = int(month)
            except ValueError:
                data['has_error'] = True
                data['error'] = 'Invalid month'
                return JsonResponse(data)

            if not month >= 1 or not month <= 12:
                data['has_error'] = True
                data['error'] = 'Invalid month'
                print(month)
                return JsonResponse(data)

            context['balance_left'] = get_balance_left(request, month)['balance_left']
            data['month'] = date(today.year, month, 1).strftime("%B")
            data['html'] = render_to_string('transactions/includes/partial_balance_left.html', context)
            return JsonResponse(data)

    per_page = settings.PAGE_SIZE
    page = request.GET.get('page', 1)
    search = request.GET.get('search', '')
    from_date = request.GET.get('from_date', str(today - timezone.timedelta(days=30)))
    to_date = request.GET.get('to_date', str(today))
    category = request.GET.get('category', '')

    filter_args = {
        'page': page,
        'search': search,
        'from_date': from_date,
        'to_date': to_date,
        'category': category,
    }

    f = TransactionFilter(filter_args, queryset=request.user.transactions.all())
    transactions = f.qs

    if output == 'excel':
        return export_to_xlsx(transactions, from_date, to_date)
    if output == 'pdf':
        return export_to_pdf(transactions, from_date, to_date)

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
        'category': category,
        'sn': sn,
        'transactions': transactions,
        'balance_left': get_balance_left(request, today.month)['balance_left'],
        'months': get_full_month_names(),
        'current_month': today.month
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


def get_balance_left(request, month):
    today = timezone.now().date()
    current_month_start = date(today.year, month, 1)
    current_month_end = date(today.year, month, monthrange(today.year, month)[1])

    balance_left = request.user.transactions\
        .filter(transaction_date__gte=current_month_start, transaction_date__lte=current_month_end)\
        .aggregate(balance_left=Sum('credit') - Sum('debit'))

    if balance_left['balance_left']:
        return balance_left
    else:
        return {'balance_left': 0.0}
