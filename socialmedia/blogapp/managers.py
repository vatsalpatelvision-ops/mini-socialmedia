from django.contrib.auth.models import BaseUserManager
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, username=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        if not username:
            raise ValueError("Username is required")
        if not password:
            raise ValueError("Password is required")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)

        if user.role == "ADMIN":
            user.is_staff = True
            user.is_superuser = True

        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, username=None, **extra_fields):
        extra_fields.setdefault("role", "ADMIN")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, username, **extra_fields)


class BlogManager(models.Manager):
    def today(self):
        today = timezone.now().date()
        return self.filter(publish_date__date=today)

    def recent(self):
        return self.order_by("-publish_date")[:3]

    def by_user(self, user):
        return self.filter(user=user)
