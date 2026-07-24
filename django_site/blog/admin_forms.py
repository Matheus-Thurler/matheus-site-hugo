from django import forms
from django.utils.translation import gettext_lazy as _


class GeneratePostAIForm(forms.Form):
    LANGUAGE_CHOICES = [
        ('both', _('English + Portuguese')),
        ('pt', _('Portuguese only')),
        ('en', _('English only')),
    ]

    brief = forms.CharField(
        label=_('What should this post cover?'),
        widget=forms.Textarea(attrs={
            'rows': 12,
            'placeholder': (
                'Example: Tutorial on using Ansible to install CloudStack on Rocky Linux 9. '
                'Cover prerequisites, playbook structure, common pitfalls, and link to my GitHub repo.'
            ),
        }),
        help_text=_('Describe the topic, audience, structure, links, and tone. The more detail, the better.'),
    )
    language = forms.ChoiceField(
        label=_('Languages'),
        choices=LANGUAGE_CHOICES,
        initial='both',
    )
    include_code = forms.BooleanField(
        label=_('Include code examples'),
        required=False,
        initial=True,
    )
