from django.db import models
from django.contrib.auth.models import Group, Permission, AbstractUser, PermissionsMixin, BaseUserManager
from django.conf import settings
from django.core.validators import RegexValidator
from django.utils.timezone import now
from django.contrib.auth.hashers import make_password

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
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[\w\s.@+-]+$',
                message="Username can only contain letters, numbers, spaces, @, ., +, -, _"
            )
        ]
    )

    role_choices = [
        ("Admin", "Admin"),           # no change
        ("Edit", "Contributor"),      # changed display name
        ("View", "Student"),          # changed display name
        ("Counsellor", "Counsellor"),  # New Role Added
    ]

    
    # Adding additional columns
    email = models.EmailField(max_length=254, unique=True)
    role = models.CharField(max_length=50, choices=role_choices, blank=True, null=True, default='View')  # Role within Consumer category
    r_level = models.IntegerField(null=True, blank=True)
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
    


#--------------------- Counsellor registration table----------------
class CounsellorProfile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='counsellor_profile',
        primary_key=True,
        # null=True,
        # blank=True
    )
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    educational_qualifications = models.TextField()
    years_of_experience_months = models.PositiveIntegerField()
    current_post = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}'s Profile"

    class Meta:
        verbose_name = "Counsellor Profile"
        verbose_name_plural = "Counsellor Profiles"