from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserManager
from django.conf import settings
# Create your models here.


class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(unique=True,max_length=150)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()
    def __str__(self):
        return self.email
    

class Blog(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    publish_date = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blogs')

    def __str__(self):
        return self.title


class Comment(models.Model):
    content = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    blog = models.ForeignKey(
        'Blog',
        on_delete=models.CASCADE,
        related_name='comments'
    )

    def __str__(self):
        return f"Comment by {self.user}"



class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='likes'
    )

    blog = models.ForeignKey(
        'Blog',
        on_delete=models.CASCADE,
        related_name='likes'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user','blog']
    
    def __str__(self):
        return f"{self.user} like {self.blog}" 