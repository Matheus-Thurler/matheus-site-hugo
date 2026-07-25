from django import forms

from .models import LinkSubmission


class LinkSubmissionForm(forms.ModelForm):
    class Meta:
        model = LinkSubmission
        fields = ('title', 'url', 'submitter_email', 'notes')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full rounded-lg border px-3 py-2'}),
            'url': forms.URLInput(attrs={'class': 'w-full rounded-lg border px-3 py-2'}),
            'submitter_email': forms.EmailInput(attrs={'class': 'w-full rounded-lg border px-3 py-2'}),
            'notes': forms.Textarea(attrs={'class': 'w-full rounded-lg border px-3 py-2', 'rows': 3}),
        }
