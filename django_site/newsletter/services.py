"""Email helpers for newsletter app."""
from django.conf import settings
from django.core.mail import EmailMultiAlternatives


def send_welcome_email(email: str, name: str, language: str = 'en') -> bool:
    """Send welcome email after subscription. Returns True if sent."""
    if not getattr(settings, 'NEWSLETTER_SEND_WELCOME', True):
        return False

    if language == 'pt':
        subject = 'Bem-vindo(a) à newsletter! 🚀'
        html = _welcome_html_pt(name)
    else:
        subject = 'Welcome to the newsletter! 🚀'
        html = _welcome_html_en(name)

    from_email = settings.NEWSLETTER_FROM_EMAIL
    from_name = settings.NEWSLETTER_FROM_NAME

    msg = EmailMultiAlternatives(
        subject=subject,
        body='',
        from_email=f'{from_name} <{from_email}>',
        to=[email],
    )
    msg.attach_alternative(html, 'text/html')

    try:
        msg.send(fail_silently=False)
        return True
    except Exception:
        return False


def _welcome_html_pt(name: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#2E3440;font-family:system-ui,sans-serif">
<div style="max-width:600px;margin:0 auto;background:#3B4252;border-radius:12px;overflow:hidden;margin-top:20px;margin-bottom:20px">
<div style="background:#2E3440;padding:30px 40px;text-align:center;border-bottom:3px solid #88C0D0">
<h1 style="margin:0;color:#ECEFF4;font-size:22px">Bem-vindo(a), {name}! 🎉</h1>
<p style="margin:6px 0 0;color:#D8DEE9;font-size:14px">Newsletter DevOps & Platform Engineering</p>
</div>
<div style="padding:30px 40px;color:#ECEFF4">
<p style="font-size:15px;line-height:1.6">Valeu por se inscrever! A partir de agora você vai receber:</p>
<ul style="font-size:14px;line-height:2;color:#D8DEE9;padding-left:20px">
<li>Tutoriais práticos de <strong style="color:#88C0D0">Google Cloud</strong> e <strong style="color:#88C0D0">Kubernetes</strong></li>
<li>Dicas de <strong style="color:#88C0D0">Terraform</strong>, CI/CD e automação</li>
<li>Novidades sobre <strong style="color:#88C0D0">AI/Gemini</strong> aplicado a DevOps</li>
<li>Curadoria semanal dos melhores conteúdos da comunidade</li>
</ul>
<p style="font-size:15px;line-height:1.6">Enquanto isso, dá uma olhada no que já publiquei:</p>
<div style="margin:20px 0">
<a href="https://youtube.com/@matheusthurler" style="display:inline-block;background:#88C0D0;color:#2E3440;padding:10px 20px;border-radius:6px;text-decoration:none;font-weight:600;font-size:14px;margin-right:8px">📺 YouTube</a>
<a href="https://matheusthurler.com.br" style="display:inline-block;background:#A3BE8C;color:#2E3440;padding:10px 20px;border-radius:6px;text-decoration:none;font-weight:600;font-size:14px">🌐 Blog</a>
</div>
<p style="font-size:14px;color:#D8DEE9;margin-top:24px">Até a próxima! 🤙</p>
<p style="font-size:14px;color:#D8DEE9"><strong>Matheus Thurler</strong><br>DevOps & Platform Engineer</p>
</div>
</div>
</body>
</html>"""


def _welcome_html_en(name: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#2E3440;font-family:system-ui,sans-serif">
<div style="max-width:600px;margin:0 auto;background:#3B4252;border-radius:12px;overflow:hidden;margin-top:20px;margin-bottom:20px">
<div style="background:#2E3440;padding:30px 40px;text-align:center;border-bottom:3px solid #88C0D0">
<h1 style="margin:0;color:#ECEFF4;font-size:22px">Welcome, {name}! 🎉</h1>
<p style="margin:6px 0 0;color:#D8DEE9;font-size:14px">DevOps & Platform Engineering Newsletter</p>
</div>
<div style="padding:30px 40px;color:#ECEFF4">
<p style="font-size:15px;line-height:1.6">Thanks for subscribing! You'll receive:</p>
<ul style="font-size:14px;line-height:2;color:#D8DEE9;padding-left:20px">
<li>Practical tutorials on <strong style="color:#88C0D0">Google Cloud</strong> and <strong style="color:#88C0D0">Kubernetes</strong></li>
<li>Tips on <strong style="color:#88C0D0">Terraform</strong>, CI/CD, and automation</li>
<li>News about <strong style="color:#88C0D0">AI/Gemini</strong> applied to DevOps</li>
<li>Weekly curation of the best community content</li>
</ul>
<p style="font-size:15px;line-height:1.6">In the meantime, check out what I've already published:</p>
<div style="margin:20px 0">
<a href="https://youtube.com/@matheusthurler" style="display:inline-block;background:#88C0D0;color:#2E3440;padding:10px 20px;border-radius:6px;text-decoration:none;font-weight:600;font-size:14px;margin-right:8px">📺 YouTube</a>
<a href="https://matheusthurler.com.br" style="display:inline-block;background:#A3BE8C;color:#2E3440;padding:10px 20px;border-radius:6px;text-decoration:none;font-weight:600;font-size:14px">🌐 Blog</a>
</div>
<p style="font-size:14px;color:#D8DEE9;margin-top:24px">See you soon! 🤙</p>
<p style="font-size:14px;color:#D8DEE9"><strong>Matheus Thurler</strong><br>DevOps & Platform Engineer</p>
</div>
</div>
</body>
</html>"""
