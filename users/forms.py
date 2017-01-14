from django import forms
from django.conf import settings
from django.contrib.auth import password_validation

from .models import User


class RegisterForm(forms.ModelForm):
    """
    Form to register a new user
    """
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'}),
        strip=False,
    )

    confirm_password = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password again'}),
        strip=False,
    )

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'username',
            'password',
            'confirm_password'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your last name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your username'}),
        }

    def clean_confirm_password(self):
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('Password mismatch')
        password_validation.validate_password(confirm_password, self.instance)
        return confirm_password

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    """
    Form to login a user
    """
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
    )

    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'}),
        strip=False,
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if email is None or email is '':
            raise forms.ValidationError("Email is required.")

        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')

        if password is None or password is '':
            raise forms.ValidationError("Password is required.")

        return password

    def clean(self):
        try:
            User.objects.get(email=self.cleaned_data.get('email'))
        except User.DoesNotExist:
            raise forms.ValidationError("Invalid login credentials.")

        return self.cleaned_data


class PasswordChangeForm(forms.Form):
    """
    Form to change user password
    """
    current_password = forms.CharField(
        label='Current Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your current password'}),
        strip=False,
    )

    new_password = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your new password'}),
        strip=False,
    )

    confirm_new_password = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your new password password'}),
        strip=False,
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(PasswordChangeForm, self).__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data["current_password"]
        if not self.user.check_password(current_password):
            raise forms.ValidationError('Incorrect current password')
        return current_password

    def clean_confirm_new_password(self):
        new_password = self.cleaned_data['new_password']
        confirm_new_password = self.cleaned_data['confirm_new_password']
        if new_password and confirm_new_password:
            if new_password != confirm_new_password:
                raise forms.ValidationError('Password mismatch')
        password_validation.validate_password(confirm_new_password, self.user)
        return confirm_new_password

    def save(self, commit=True):
        password = self.cleaned_data["confirm_new_password"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user


class SendPasswordResetEmailForm(forms.Form):
    """
    Form to send password reset email
    """
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
    )

    def __init__(self, *args, **kwargs):
        self.user = None
        super(SendPasswordResetEmailForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        try:
            self.user = User.objects.get(email=self.cleaned_data['email'])
        except User.DoesNotExist:
            raise forms.ValidationError("No account associated with this email.")

        return self.cleaned_data['email']

    def save(self):
        if not settings.DEBUG:
            self.user.send_password_reset_email()


class PasswordResetForm(forms.Form):
    """
    Form to reset user's password
    """
    new_password = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your new password'}),
        strip=False,
    )

    confirm_new_password = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your new password password'}),
        strip=False,
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(PasswordResetForm, self).__init__(*args, **kwargs)

    def clean_confirm_new_password(self):
        new_password = self.cleaned_data['new_password']
        confirm_new_password = self.cleaned_data['confirm_new_password']
        if new_password and confirm_new_password:
            if new_password != confirm_new_password:
                raise forms.ValidationError('Password mismatch')
        return confirm_new_password

    def save(self):
        password = self.cleaned_data["confirm_new_password"]
        self.user.set_password(password)
        self.user.save()
        return self.user
