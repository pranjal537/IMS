from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm as DjangoPasswordChangeForm
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class LoginForm(forms.Form):
    """
    Email + password login form for Damak Municipality IMS.
    Uses email as the login identifier.
    """
    email = forms.EmailField(
        label=_('Email Address'),
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'id': 'emailInput',
            'placeholder': 'e.g. supervisor@damak.gov.np',
            'autocomplete': 'email',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label=_('Password'),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'id': 'passwordInput',
            'placeholder': '••••••••',
            'autocomplete': 'current-password',
        })
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        from django.contrib.auth import authenticate
        email = self.cleaned_data.get('email', '').lower().strip()
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(
                self.request,
                username=email,
                password=password
            )
            if self.user_cache is None:
                # Generic error — do not reveal if email exists
                raise forms.ValidationError(
                    _('Invalid email or password. Please check your credentials and try again.'),
                    code='invalid_login',
                )
            if not self.user_cache.is_active:
                raise forms.ValidationError(
                    _('This account has been deactivated. Please contact the administrator.'),
                    code='inactive',
                )
        return self.cleaned_data

    def get_user(self):
        return self.user_cache


class ImsPasswordChangeForm(DjangoPasswordChangeForm):
    """
    Styled password change form for Damak Municipality IMS.
    Wraps Django's built-in PasswordChangeForm with Bootstrap styling.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        widget_attrs = {
            'class': 'form-control',
            'autocomplete': 'off',
        }
        self.fields['old_password'].widget.attrs.update({
            **widget_attrs,
            'id': 'oldPasswordInput',
            'placeholder': 'Current password',
        })
        self.fields['new_password1'].widget.attrs.update({
            **widget_attrs,
            'id': 'newPassword1Input',
            'placeholder': 'New password',
        })
        self.fields['new_password2'].widget.attrs.update({
            **widget_attrs,
            'id': 'newPassword2Input',
            'placeholder': 'Confirm new password',
        })
