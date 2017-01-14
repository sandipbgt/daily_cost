from django.conf.urls import url, include

from . import views

app_name = "users"

urlpatterns = [
    url(r'^login/$', views.user_login, name='login'),
    url(r'^register/$', views.user_register, name='register'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^confirm_email/$', views.user_email_confirm, name='email_confirm'),
    url(r'^change_password/$', views.user_password_change, name='password_change'),
    url(r'^send_password_reset_email/$', views.user_send_password_reset_email, name='send_password_reset_email'),
    url(r'^password_reset/$', views.user_password_reset, name='password_reset'),
]
