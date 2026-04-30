from .models import Blog , Notifications
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

@receiver(post_save, sender=Blog)
def create_blog_notification(sender, instance, created, **kwargs):
    if created:
        Notifications.objects.create(
            user = instance.user,
            message = f"New blog created : {instance.title}",
            blog = instance
        )

        print("Blog created")


@receiver(pre_delete, sender=Blog)
def delete_blog_notification(sender, instance, **kwargs):
    Notifications.objects.create(
        user = instance.user,
        message = f"Blog deleted : {instance.title}",
        blog = instance
    )

    print("Blog deleted")