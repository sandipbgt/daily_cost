from functools import reduce

import django_filters
from django.db.models import Q

from .models import Transaction


class TransactionFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(name='category__name', lookup_expr='icontains')
    search = django_filters.CharFilter(name='title', method='search_transaction')
    from_date = django_filters.DateFilter(name='transaction_date', lookup_expr='gte')
    to_date = django_filters.DateFilter(name='transaction_date', lookup_expr='lte')

    def search_transaction(self, queryset, name, value):
        values = value.split()
        return queryset\
            .filter(
                reduce(Q.__or__, [Q(title__icontains=query) for query in values]) |
                reduce(Q.__or__, [Q(category__name__icontains=query) for query in values])
            ).distinct()

    class Meta:
        model = Transaction
        fields = [
            'category',
            'search',
            'from_date',
            'to_date',
        ]
