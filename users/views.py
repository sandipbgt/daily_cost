import jwt
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect
from django.contrib import messages

from users.models import User
from .forms import (
    RegisterForm,
    LoginForm,
    PasswordChangeForm,
    PasswordResetForm,
    SendPasswordResetEmailForm,)


def user_register(request):
    """
    Register a user
    """
    if request.user.is_authenticated():
        return redirect('dashboard')

    form = RegisterForm(data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            messages.success(request, "We have sent you confirmation email \
                Please confirm your account by clicking on the confirmation link \
                sent to your email.")
            return redirect('users:login')

    context = {
        'form': form
    }
    return render(request, 'users/register.html', context)


def user_login(request):
    """
    Login a user
    """
    if request.user.is_authenticated():
        return redirect('dashboard')

    form = LoginForm(data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            user = authenticate(username=email, password=password)
            if user is None:
                messages.error(request, "Invalid login credentials")
                return redirect('users:login')
            else:
                if not user.is_confirmed:
                    messages.warning(request, "Email not confirmed. Please confirm your account by " +
                                     "clicking on the activation link sent to your email.")
                    return redirect('users:login')

                login(request, user)

                return redirect('dashboard')

    context = {
        'form': form,
    }

    return render(request, 'users/login.html', context)


def user_email_confirm(request):
    """
    Confirm user's email
    """
    if request.user.is_authenticated():
        return redirect('dashboard')

    token = request.GET.get('token')
    if token is None:
        raise Http404()

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithm='HS256')
    except jwt.ExpiredSignature:
        messages.error(request, 'Confirmation token has expired.')
        return redirect('home')
    except jwt.DecodeError:
        messages.error(request, 'Error decoding confirmation token.')
        return redirect('home')
    except jwt.InvalidTokenError:
        messages.error(request, 'Invalid confirmation token.')
        return redirect('home')

    try:
        user = User.objects.get(pk=payload['confirm'])
    except User.DoesNotExist:
        messages.error(request, 'Account not found.')
        return redirect('home')

    if user.is_confirmed:
        messages.error(request, "Email already confirmed.")
    else:
        user.is_confirmed = True
        user.save()
        messages.success(request, "Email confirmed.")
    return redirect('users:login')


@login_required
def user_password_change(request):
    """
    Change user password
    """
    form = PasswordChangeForm(data=request.POST or None, user=request.user)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Password changed successfully")
            return redirect('user_password_change')

    context = {
        'form': form
    }
    return render(request, 'users/change_password.html', context)


def user_send_password_reset_email(request):
    """
    Send password reset email
    """
    if request.user.is_authenticated():
        return redirect('dashboard')

    form = SendPasswordResetEmailForm(data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Password reset email sent. Please check your email for instructions.")
            return redirect('users:send_password_reset_email')

    context = {
        'form': form
    }
    return render(request, 'users/send_password_reset_email.html', context)


def user_password_reset(request):
    """
    Reset user password
    """
    if request.user.is_authenticated():
        return redirect('dashboard')

    token = request.GET.get('token')
    if token is None:
        raise Http404()

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithm='HS256')
    except jwt.ExpiredSignature:
        messages.error(request, 'Reset token has expired.')
        return redirect('users:send_password_reset_email')
    except jwt.DecodeError:
        messages.error(request, 'Error decoding reset token.')
        return redirect('users:send_password_reset_email')
    except jwt.InvalidTokenError:
        messages.error(request, 'Invalid reset token.')
        return redirect('users:send_password_reset_email')

    try:
        user = User.objects.get(pk=payload['reset'])
    except User.DoesNotExist:
        messages.error(request, 'Invalid token.')
        return redirect('users:send_password_reset_email')

    form = PasswordResetForm(data=request.POST or None, user=user)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Password reset successfully.")
            return redirect('users:login')

    context = {
        'form': form
    }
    return render(request, 'users/password_reset.html', context)


@login_required
def user_logout(request):
    """
    Logout a user
    """
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('users:login')



