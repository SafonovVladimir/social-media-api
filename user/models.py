import os
import uuid
from datetime import date

from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.utils.translation import gettext as _
from django.contrib.auth.models import AbstractUser, BaseUserManager


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)

    @property
    def full_name(self):
        return self.first_name + " " + self.last_name


class User(AbstractUser):
    """User model."""

    username = None
    email = models.EmailField(_("email address"), unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()


def movie_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{uuid.uuid4()}{extension}"
    return os.path.join(f"uploads/profiles/{slugify(instance.user.email)}",
                        filename)


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    bio = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, default="")
    phone = models.IntegerField(default=0)
    birthday = models.DateField(default=date.today, blank=True)
    image = models.ImageField(null=True, upload_to=movie_image_file_path)
    followers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="profiles"
    )

    def __str__(self):
        return self.user.email
