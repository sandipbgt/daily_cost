from django.db import models

from categories.models import Category
from users.models import User


class Transaction(models.Model):
    """
    Transaction model
    """
    user = models.ForeignKey(User, related_name="transactions", on_delete=models.CASCADE)
    category = models.ForeignKey(Category, related_name="transactions", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=15, choices=(
        ('Income', 'Income'),
        ('Expense', 'Expense')
    ))
    debit = models.DecimalField(max_digits=15, decimal_places=2)
    credit = models.DecimalField(max_digits=15, decimal_places=2)
    transaction_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'transactions'
        ordering = ['-transaction_date', '-created_at']

    def __str__(self):
        return self.title
