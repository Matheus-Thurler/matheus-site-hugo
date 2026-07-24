from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = ContactMessage
        fields = ('name', 'email', 'subject', 'message')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full rounded-lg border border-border bg-card px-3 py-2'}),
            'email': forms.EmailInput(attrs={'class': 'w-full rounded-lg border border-border bg-card px-3 py-2'}),
            'subject': forms.TextInput(attrs={'class': 'w-full rounded-lg border border-border bg-card px-3 py-2'}),
            'message': forms.Textarea(attrs={'class': 'w-full rounded-lg border border-border bg-card px-3 py-2', 'rows': 6}),
        }

    def clean_website(self):
        if self.cleaned_data.get('website'):
            raise forms.ValidationError('Spam detected.')
        return ''
