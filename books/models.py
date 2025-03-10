from django.db import models
from accounts.models import User

# Create your models here.
class Books(models.Model):
    name = models.CharField(max_length=255)
    version = models.CharField(max_length=50)
    created_by = models.ForeignKey(User, related_name='books_created', on_delete=models.SET_NULL, null=True)
    updated_by = models.ForeignKey(User, related_name='books_updated', on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)  # Auto-updates on modification

class Descriptions(models.Model):
    book = models.ForeignKey(Books, related_name='descriptions', on_delete=models.CASCADE)
    code = models.CharField(max_length=50)
    description = models.TextField()
    created_by = models.ForeignKey(User, related_name='descriptions_created', on_delete=models.SET_NULL, null=True)
    updated_by = models.ForeignKey(User, related_name='descriptions_updated', on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)

class SubDescriptions(models.Model):
    description = models.ForeignKey(Descriptions, related_name='sub_descriptions', on_delete=models.CASCADE)
    code = models.CharField(max_length=50)
    sub_description = models.TextField()
    created_by = models.ForeignKey(User, related_name='sub_descriptions_created', on_delete=models.SET_NULL, null=True)
    updated_by = models.ForeignKey(User, related_name='sub_descriptions_updated', on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)

class History(models.Model):
    model_name = models.CharField(max_length=255)  # e.g., "Books", "Descriptions"
    record_id = models.PositiveIntegerField()  # Stores the ID of the modified record
    changes = models.JSONField()  # Stores previous values before update
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now_add=True)  # Stores modification timestamp
