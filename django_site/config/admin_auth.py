from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _


class AdminEmailLoginForm(AuthenticationForm):
    username = forms.CharField(
        label=_('Usuário ou e-mail'),
        widget=forms.TextInput(attrs={'autofocus': True, 'autocomplete': 'username'}),
    )
