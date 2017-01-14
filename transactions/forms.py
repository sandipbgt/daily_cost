from django import forms
from django.utils import timezone

from categories.models import Category
from .models import Transaction


class ExpenseForm(forms.ModelForm):
    """
    Form to add expense
    """
    category = forms.ModelChoiceField(
        label='Category',
        queryset=Category.objects.none(),
        empty_label='Select Category',
        widget=forms.Select(attrs={'class': 'form-control'}),
        error_messages={
            'invalid_choice': 'Invalid category'
        }
    )

    class Meta:
        model = Transaction
        fields = [
            'transaction_date',
            'category',
            'title',
            'debit',
        ]
        widgets = {
            'transaction_date': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter date'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title'}),
            'debit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter amount'}),
        }
        labels = {
            'debit': 'Amount'
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ExpenseForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = self.user.categories

    def save(self, commit=True):
        expense = super(ExpenseForm, self).save(commit=False)
        expense.user = self.user
        expense.type = 'Expense'
        expense.credit = 0.0
        if commit:
            expense.save()
        return expense


class IncomeForm(forms.ModelForm):
    """
    Form to add income
    """
    category = forms.ModelChoiceField(
        label='Category',
        queryset=Category.objects.none(),
        empty_label='Select Category',
        widget=forms.Select(attrs={'class': 'form-control'}),
        error_messages={
            'invalid_choice': 'Invalid category'
        }
    )

    class Meta:
        model = Transaction
        fields = [
            'transaction_date',
            'category',
            'title',
            'credit',
        ]
        widgets = {
            'transaction_date': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter date'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title'}),
            'credit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter amount'}),
        }
        labels = {
            'credit': 'Amount'
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(IncomeForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = self.user.categories

    def save(self, commit=True):
        income = super(IncomeForm, self).save(commit=False)
        income.user = self.user
        income.type = 'Income'
        income.debit = 0.0
        if commit:
            income.save()
        return income
