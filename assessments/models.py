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



class QuizName(models.Model):
    quiz_name = models.CharField(max_length=100, null=True, blank=True, default="Unnamed Quiz")
    category_1 = models.CharField(max_length=100)
    category_2 = models.CharField(max_length=100)
    category_3 = models.CharField(max_length=100)
    category_4 = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=
                            [("question-based", "Question-Based"), 
                             ("statement-based", "Statement-Based")
                             ], default="question-based")
   
    def __str__(self):
        return f"{self.quiz_name} | {self.category_1} | {self.category_2} | {self.category_3} | {self.category_4}"


class NewQuiz(models.Model):
    question = models.TextField(null=True, blank=True)
    option_1 = models.CharField(max_length=255)
    option_2 = models.CharField(max_length=255)
    option_3 = models.CharField(max_length=255)
    option_4 = models.CharField(max_length=255)
    quiz = models.ForeignKey(QuizName, on_delete=models.CASCADE, related_name='questions')

    def __str__(self):
        return self.question or "No Question"
    

class QuizResult(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    quiz = models.ForeignKey(QuizName, on_delete=models.CASCADE)
    cat_1_marks = models.IntegerField(default=0)
    cat_2_marks = models.IntegerField(default=0)
    cat_3_marks = models.IntegerField(default=0)
    cat_4_marks = models.IntegerField(default=0)
    skip = models.IntegerField()
    result = models.CharField(max_length=100, blank=True, null=True)
    date_taken = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.quiz_name} - {self.score}"