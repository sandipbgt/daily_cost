"""daily_cost URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include

from pages import views as page_views

urlpatterns = [
    url('^$', page_views.home, name='home'),
    url('^dashboard/$', page_views.dashboard, name='dashboard'),

    url('^users/', include('users.urls')),
    url(r'^categories/', include('categories.urls')),
    url(r'^transactions/', include('transactions.urls')),
]
