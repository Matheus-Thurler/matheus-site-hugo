from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'w-full p-3 border border-border rounded-lg bg-background text-foreground',
                'placeholder': 'Escreva seu comentário...',
                'rows': 4,
            }),
        }
