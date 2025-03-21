from django.db import models
from accounts.models import User    

class CommonQuestion(models.Model):
    # id = models.AutoField(primary_key=True)
    question = models.TextField()

    logical = models.CharField(max_length=255)
    analytical = models.CharField(max_length=255)
    strategic = models.CharField(max_length=255)
    thinking = models.CharField(max_length=255)

    def __str__(self):
        return self.question

class CommonTest(models.Model):
    # id = models.AutoField(primary_key=True)
    logical = models.IntegerField()
    analytical = models.IntegerField()
    strategic = models.IntegerField()
    thinking = models.IntegerField()
    skip = models.IntegerField()
    total = models.IntegerField()   
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)  # Stores creation timestamp
    updated_at = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return self.user
