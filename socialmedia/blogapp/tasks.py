from celery import shared_task
from django.core.mail import send_mail
from django.core.cache import cache


@shared_task
def send_email_welcome(user_email):
    send_mail(
        subject="Welcome!",
        message="Thanks for registering 🎉",
        from_email="noreply@example.com",
        recipient_list=[user_email],
    )


@shared_task
def clear_blog_cache(blog_id=None):
    cache.delete("cached_blog_list")
    if blog_id:
        cache.delete(f"cached_blog_detail_{blog_id}")
