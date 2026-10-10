from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import EmailMessage

from .portfolio import load_projects


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
        
        # 1. CHECK THE HONEYPOT FIRST!
        honeypot = request.POST.get('website_url', '')
        if honeypot != '':
            # A bot filled it out! Pretend it worked, but do NOT send the email.
            messages.success(request, 'Thank you! Your quote request has been sent.')
            return redirect('home')

        # 2. Get the real data (if the honeypot was blank)
        name = request.POST['full_name']
        email = request.POST['email']
        phone = request.POST['phone']
        subject = request.POST['subject']
        message = request.POST['message']

        # 3. Construct the email body
        email_body = f"""
        You have received a new Quote Request / Inquiry from AUestate Drafting & Design.
        
        Name: {name}
        Email: {email}
        Phone: {phone}
        Subject: {subject}
        
        Message:
        {message}
        """

        # 4. Send the email
        email_msg = EmailMessage(
            subject=f'Drafting Inquiry: {subject}',
            body=email_body,
            from_email='admin@auestate.com.au',
            to=['admin@auestate.com.au'],
            reply_to=[email], 
        )
        email_msg.send(fail_silently=False)

        messages.success(request, 'Thank you! Your quote request has been sent.')
        return redirect('home')

    return render(request, 'pages/general_contact.html')