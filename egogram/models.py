from django.db import models
from accounts.models import User
# Create your models here.

class Category(models.Model):
    category = models.CharField(max_length=255)
    category_description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.category
    

class EgogramTest(models.Model):
    test_name = models.CharField(max_length=255)
    test_description = models.TextField(blank=True, null=True)
    statements = models.ManyToManyField('EgogramStatement', related_name='tests')

    def __str__(self):
        return self.test_name
    

class EgogramStatement(models.Model):
    statement = models.TextField()
    category = models.ForeignKey(
    'egogram.Category',  # use app_label.ModelName
    on_delete=models.CASCADE,
    related_name='category_items'
    )
    # test = models.ForeignKey(
    #     EgogramTest,
    #     on_delete=models.CASCADE,
    #     related_name='test_items'
    # )

    def __str__(self):
        return f"{self.statement[:50]}..."  # Shows first 50 chars of statement
    

class ResultHistory(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='egogram_results'
    )
    statement_marks = models.JSONField(
        help_text="JSON storing statement IDs and their marks"
    )
    final_result = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name="top_results"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Result for {self.user.email} on {self.created_at}"
