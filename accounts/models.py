from django.db import models
from django.contrib.auth.models import Group, Permission, AbstractUser, PermissionsMixin, BaseUserManager
from django.conf import settings
from django.utils.timezone import now

# Create your models here.
class UserManager(BaseUserManager):

    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        if not password:
            raise ValueError('Password is not provided')
        
        user = self.model(
            email=self.normalize_email(email),
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        user = self._create_user(email, password, True, True, **extra_fields)
        return user


class User(AbstractUser, PermissionsMixin):

    role_choices = [
        ("Admin", "Admin"),
        ("Edit", "Edit"),
        ("View", "View"),
    ]
    
    # Adding additional columns
    email = models.EmailField(max_length=254, unique=True)
    role = models.CharField(max_length=50, choices=role_choices, blank=True, null=True, default='View')  # Role within Consumer category
    email_otp = models.CharField(max_length=6, blank=True, null=True)  # Email OTP for Consumer users
    verified_at = models.DateTimeField(blank=True, null=True)  # Verification timestamp
    registration_token = models.CharField(max_length=64, blank=True, null=True)  # Token for password setup

    # Define custom related names for groups and user_permissions
    groups = models.ManyToManyField(Group, related_name='custom_user_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_permissions', blank=True)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email