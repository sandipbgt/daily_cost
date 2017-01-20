import django_filters

from .models import Transaction


class TransactionFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(name='title', lookup_expr='icontains')
    from_date = django_filters.DateFilter(name='transaction_date', lookup_expr='gte')
    to_date = django_filters.DateFilter(name='transaction_date', lookup_expr='lte')

    class Meta:
        model = Transaction
        fields = [
            'search',
            'from_date',
            'to_date',
        ]
