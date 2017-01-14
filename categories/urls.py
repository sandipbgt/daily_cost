from django.conf.urls import url

from . import views

app_name = "categories"

urlpatterns = [
    url(r'^$', views.category_list, name='list'),
    url(r'^new/$', views.category_create, name='create'),
    url(r'^(?P<pk>[0-9]+)/edit/$', views.category_edit, name='edit'),
    url(r'^(?P<pk>[0-9]+)/delete/$', views.category_delete, name='delete'),
]
