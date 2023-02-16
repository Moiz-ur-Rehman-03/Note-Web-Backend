from django.conf import settings
from django.core.mail import EmailMessage


def send_email(subject, message, emails):
    email = EmailMessage(subject, message, settings.EMAIL_HOST_USER, emails)
    email.send()
