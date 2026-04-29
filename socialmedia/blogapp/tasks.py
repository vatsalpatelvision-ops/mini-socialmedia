from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_email_welcome(user_email):
    send_mail(
        subject="Welcome!",
        message="Thanks for registering 🎉",
        from_email="noreply@example.com",
        recipient_list=[user_email],
    )