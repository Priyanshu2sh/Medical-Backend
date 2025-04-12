from django.db import models
from accounts.models import User

class Books(models.Model):
    name = models.CharField(max_length=255)
    version = models.CharField(max_length=50)
    author = models.CharField(max_length=255, null=True)  # New author field
    code_sets = models.JSONField(default=list)  # Stores array of strings
    created_by = models.ForeignKey(User, related_name='books_created', on_delete=models.SET_NULL, null=True)
    updated_by = models.ForeignKey(User, related_name='books_updated', on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)  # Auto-updates on modification

class Descriptions(models.Model):
    book = models.ForeignKey(Books, related_name='descriptions', on_delete=models.CASCADE)
    code = models.CharField(max_length=50)
    description = models.TextField() 
    like_count = models.PositiveIntegerField(default=0)
    dislike_count = models.PositiveIntegerField(default=0)           
    created_by = models.ForeignKey(User, related_name='descriptions_created', on_delete=models.SET_NULL, null=True)
    updated_by = models.ForeignKey(User, related_name='descriptions_updated', on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)

class SubDescriptions(models.Model):
    description = models.ForeignKey(Descriptions, related_name='sub_descriptions', on_delete=models.CASCADE)
    code = models.CharField(max_length=50)
    sub_description = models.TextField()
    sub_data = models.TextField(null=True, blank=True)  
    created_by = models.ForeignKey(User, related_name='sub_descriptions_created', on_delete=models.SET_NULL, null=True)
    updated_by = models.ForeignKey(User, related_name='sub_descriptions_updated', on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)

class History(models.Model):
    model_name = models.CharField(max_length=255)  # e.g., "Books", "Descriptions"
    record_id = models.PositiveIntegerField()  # Stores the ID of the modified record
    changes = models.JSONField()  # Stores previous values before update
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now_add=True)  # Stores modification timestamp


class CodeReaction(models.Model):
    description = models.ForeignKey(Descriptions, related_name='reactions', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='code_reactions', on_delete=models.CASCADE)
    like = models.BooleanField(default=False)
    dislike = models.BooleanField(default=False)

    class Meta:
        unique_together = ('description', 'user')  # Ensures a user can only react once per description
