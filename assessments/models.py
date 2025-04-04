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
    TEST_TYPES = [
        ("mcq", "MCQ"),
        ("statement-based", "Statement-Based"),
    ]
    # id = models.AutoField(primary_key=True)
    logical = models.IntegerField()
    analytical = models.IntegerField()
    strategic = models.IntegerField()
    thinking = models.IntegerField()
    skip = models.IntegerField()
    total = models.IntegerField()   
    result = models.CharField(max_length=100, blank=True, null=True)   
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=TEST_TYPES, default="mcq")  
    created_at = models.DateTimeField(auto_now_add=True)  # Stores creation timestamp
    updated_at = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return str(self.user)

class StatementOption(models.Model):
    logical = models.CharField(max_length=255)
    analytical = models.CharField(max_length=255)
    strategic = models.CharField(max_length=255)
    thinking = models.CharField(max_length=255)

    def __str__(self):
        return f"Logical: {self.logical}, Analytical: {self.analytical}, Strategic: {self.strategic}, Thinking: {self.thinking}"

        