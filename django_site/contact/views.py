from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from django_ratelimit.decorators import ratelimit

from .forms import ContactForm


def _client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


@ratelimit(key='ip', rate='5/h', method='POST', block=True)
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.ip_address = _client_ip(request)
            msg.save()
            send_mail(
                subject=f'[Contact] {msg.subject}',
                message=f'From: {msg.name} <{msg.email}>\n\n{msg.message}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.NEWSLETTER_FROM_EMAIL],
                fail_silently=True,
            )
            messages.success(request, _('Message sent! I will reply soon.'))
            return redirect('contact:contact')
    else:
        form = ContactForm()
    return render(request, 'contact/contact.html', {'form': form})
