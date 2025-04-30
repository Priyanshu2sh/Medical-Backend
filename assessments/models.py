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
    cat_1_marks = models.IntegerField(default=0, null=True, blank=True)
    cat_2_marks = models.IntegerField(default=0 ,null=True, blank=True)
    cat_3_marks = models.IntegerField(default=0 ,null=True, blank=True)
    cat_4_marks = models.IntegerField(default=0 ,null=True, blank=True)
    skip = models.IntegerField()
    result = models.CharField(max_length=100, blank=True, null=True)
    date_taken = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.quiz_name} - {self.score}"
    

class McqQuiz(models.Model):
    SINGLE_CHOICE = 'single-choice'
    MULTIPLE_CHOICE = 'multiple-choice'
    QUIZ_TYPE_CHOICES = [
        (SINGLE_CHOICE, 'Single Choice'),
        (MULTIPLE_CHOICE, 'Multiple Choice'),
    ]

    type = models.CharField(max_length=20, choices=QUIZ_TYPE_CHOICES)
    name = models.CharField(max_length=255)
    description = models.TextField()

    question = models.ForeignKey(
        'McqQuestions',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quiz_reference'
    )

    # questions = models.ManyToManyField('McqQuestions', related_name='quizzes')

    def __str__(self):
        return self.name
    

class McqQuestions(models.Model):
    SINGLE_CHOICE = 'single-choice'
    MULTIPLE_CHOICE = 'multiple-choice'
    QUESTION_TYPE_CHOICES = [
        (SINGLE_CHOICE, 'Single Choice'),
        (MULTIPLE_CHOICE, 'Multiple Choice'),
    ]
    quiz = models.ForeignKey(McqQuiz, on_delete=models.CASCADE, related_name="questions", null=True, blank=True)
    question = models.TextField()
    options_1 = models.CharField(max_length=255)
    options_2 = models.CharField(max_length=255)
    options_3 = models.CharField(max_length=255)
    options_4 = models.CharField(max_length=255)
    
    correct_ans = models.JSONField(help_text="Store correct answer(s) as JSON. For example: ['option_1'] or ['option_2', 'option_3']")
    type = models.CharField(
        max_length=20,
        choices=QUESTION_TYPE_CHOICES,
        default=SINGLE_CHOICE,
        help_text="Define whether the question is single or multiple choice"
    )


    def __str__(self):
        return self.question


class McqQuizResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(QuizName, on_delete=models.CASCADE)
    score = models.PositiveIntegerField()
    total_questions = models.PositiveIntegerField()
    skip_questions = models.PositiveIntegerField(default=0)  
    performance = models.CharField(max_length=50, blank=True) 
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.name} - {self.score}/{self.total_questions}"