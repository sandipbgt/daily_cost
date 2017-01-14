from django.conf.urls import url

from . import views

app_name = "transactions"

urlpatterns = [
    url(r'^$', views.transaction_list, name='list'),
    url(r'^expenses/new/$', views.expense_create, name='expense_create'),
    url(r'^incomes/new/$', views.income_create, name='income_create'),
    url(r'^(?P<pk>[0-9]+)/edit/$', views.transaction_edit, name='edit'),
    url(r'^(?P<pk>[0-9]+)/delete/$', views.transaction_delete, name='delete'),
]
