from django.db import models
import random
# from django.db.models.functions import Random

class MCQ(models.Model):
    question = models.TextField()
    option1 = models.CharField(max_length=255)
    option2 = models.CharField(max_length=255)
    option3 = models.CharField(max_length=255)
    option4 = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=255)

    def __str__(self):
        return self.question

    # import random

    @classmethod
    def get_random_questions(cls, count=40):
        """Fetch 40 random questions"""
        ids = list(cls.objects.values_list('id', flat=True))
        random_ids = random.sample(ids, min(len(ids), count))
        return cls.objects.filter(id__in=random_ids)