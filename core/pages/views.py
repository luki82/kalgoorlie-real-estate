import logging

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render

from .models import Inquiry
from .portfolio import load_projects

logger = logging.getLogger(__name__)


def home(request):
    projects = load_projects()
    return render(request, 'pages/home.html', {'latest': projects[0] if projects else None})


def portfolio(request):
    return render(request, 'pages/portfolio.html', {'projects': load_projects()})


def about(request):
    return render(request, 'pages/about.html')


def services(request):
    return render(request, 'pages/services.html')


def terms(request):
    return render(request, 'pages/terms.html')


def general_contact(request):
    if request.method == 'POST':

        # 1. Check the honeypot first: a hidden field only bots fill in.
        if request.POST.get('website_url', ''):
            messages.success(request, 'Thank you! Your quote request has been sent.')
            return redirect('home')

        # 2. Read the form.
        name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if not (name and email and message):
            messages.error(request, 'Please fill in your name, email and message.')
            return render(request, 'pages/general_contact.html', status=400)

        # 3. Save it first, so no enquiry is ever lost (see Inquiries in admin).
        inquiry = Inquiry.objects.create(
            full_name=name[:100], email=email[:254], phone=phone[:30],
            subject=subject[:200], message=message,
        )

        # 4. Email it. If email isn't working, the enquiry is still saved.
        email_body = (
            "You have received a new quote request / enquiry from the drafting website.\n\n"
            f"Name: {name}\nEmail: {email}\nPhone: {phone}\nSubject: {subject}\n\n"
            f"Message:\n{message}\n"
        )
        try:
            EmailMessage(
                subject=f'Drafting Inquiry: {subject or name}',
                body=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.CONTACT_EMAIL],
                reply_to=[email],
            ).send(fail_silently=False)
        except Exception:
            logger.exception('Contact form email failed; enquiry %s saved in admin', inquiry.pk)
        else:
            inquiry.email_sent = True
            inquiry.save(update_fields=['email_sent'])

        messages.success(request, 'Thank you! Your quote request has been sent.')
        return redirect('home')

    return render(request, 'pages/general_contact.html')
