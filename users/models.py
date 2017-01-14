from datetime import datetime, timedelta

import jwt
import requests

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.conf import settings

from .validators import UsernameValidator


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError("User must have a valid email address.")

        if not kwargs.get('username'):
            raise ValueError('User must have a valid username')

        user = self.model(
            username=kwargs.get('username').strip(),
            email=self.normalize_email(email),
            first_name=kwargs.get('first_name', None),
            last_name=kwargs.get('last_name', None),
            is_confirmed=kwargs.get('is_confirmed', False),
        )

        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password, **kwargs):
        user = self.create_user(email, password, **kwargs)
        user.save()

        return user


class User(AbstractBaseUser):
    """
    User model
    """
    username = models.CharField(
        max_length=255,
        unique=True,
        validators=[UsernameValidator()],
        error_messages={
            'unique': 'User with this username already exists.',
        },
    )
    email = models.EmailField(
        unique=True,
        error_messages={
            'unique': 'User with this email already exists.',
        },
    )
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40)
    is_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def get_full_name(self):
        return ' '.join([self.first_name, self.last_name])

    def get_short_name(self):
        return self.first_name

    def generate_confirmation_token(self):
        payload = {
            'confirm': self.id,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(days=7)
        }

        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256').decode('utf-8')
        return token

    def send_confirmation_email(self):
        token = self.generate_confirmation_token()
        link = settings.BASE_URL + '/users/confirm_email?token={}'.format(token)
        html = '<html>Click on the below link to confirm your email. <a href="{}">{}</a></html>'.format(link, link)
        data = {
            'from': "{} <{}>".format('Daily Cost', settings.ADMIN_EMAIL),
            'to': self.email,
            'subject': "Email Confirmation",
            'html': html
        }

        requests.post(settings.MAILGUN_SERVER,
                auth=("api", settings.MAILGUN_API_KEY),
                data=data)

    def generate_password_reset_token(self):
        payload = {
            'reset': self.id,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(days=7)
        }

        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256').decode('utf-8')
        return token

    def send_password_reset_email(self):
        token = self.generate_password_reset_token()
        link = settings.BASE_URL + '/users/password_reset?token={}'.format(token)
        html = '<html>Click on the below link to reset your password. <a href="{}">{}</a></html>'.format(link, link)
        data = {
            'from': "{} <{}>".format('Daily Cost', settings.ADMIN_EMAIL),
            'to': self.email,
            'subject': "Reset Password",
            'html': html
        }

        requests.post(settings.MAILGUN_SERVER,
                auth=("api", settings.MAILGUN_API_KEY),
                data=data)

    def __str__(self):
        return self.email

    class Meta:
        db_table = "users"
