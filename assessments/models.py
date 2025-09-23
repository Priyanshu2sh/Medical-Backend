from django.db import models
from egogram.models import Category  # Import the Category model  
from django.contrib.auth.hashers import make_password, check_password

class MedicalHealthUser(models.Model):
    role_choices = [
        ("user", "user"),
        ("Counsellor", "Counsellor"),
        ("admin", "admin")
    ]

    status_choices = [
        ("Active", "Active"),
        ("Inactive", "Inactive"),
    ]

    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    username = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  # store hashed password
    role = models.CharField(max_length=20, choices=role_choices, default="user")
    otp = models.CharField(max_length=6, blank=True, null=True)
    verified_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=status_choices, default="Active")

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def save(self, *args, **kwargs):
        # If password is not already hashed, hash it before saving
        if not self.password.startswith('pbkdf2_'):  # simple check for hashed pw prefix
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

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
    user_id = models.ForeignKey(MedicalHealthUser, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=TEST_TYPES, default="mcq")  
    created_at = models.DateTimeField(auto_now_add=True)  # Stores creation timestamp
    updated_at = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return str(self.user_id)

class StatementOption(models.Model):
    logical = models.CharField(max_length=255)
    analytical = models.CharField(max_length=255)
    strategic = models.CharField(max_length=255)
    thinking = models.CharField(max_length=255)

    def __str__(self):
        return f"Logical: {self.logical}, Analytical: {self.analytical}, Strategic: {self.strategic}, Thinking: {self.thinking}"


#personality test 
class QuizName(models.Model):
    quiz_name = models.CharField(max_length=100, null=True, blank=True, default="Unnamed Quiz")
    quiz_description = models.TextField(null=True, blank=True)
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
    
    # add column 


class NewQuiz(models.Model):
    question = models.TextField(null=True, blank=True)
    option_1 = models.CharField(max_length=255, null=True, blank=True)
    option_2 = models.CharField(max_length=255, null=True, blank=True)
    option_3 = models.CharField(max_length=255, null=True, blank=True)
    option_4 = models.CharField(max_length=255, null=True, blank=True)
    quiz = models.ForeignKey(QuizName, on_delete=models.CASCADE, related_name='questions')

    def __str__(self):
        return self.question or "No Question"
    

class QuizResult(models.Model):
    user_id = models.ForeignKey(MedicalHealthUser, on_delete=models.CASCADE, null=True, blank=True)
    quiz = models.ForeignKey(QuizName, on_delete=models.CASCADE)
    cat_1_marks = models.IntegerField(default=0, null=True, blank=True)
    cat_2_marks = models.IntegerField(default=0 ,null=True, blank=True)
    cat_3_marks = models.IntegerField(default=0 ,null=True, blank=True)
    cat_4_marks = models.IntegerField(default=0 ,null=True, blank=True)
    skip = models.IntegerField()
    result = models.CharField(max_length=100, blank=True, null=True)
    date_taken = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_id.first_name} - {self.quiz.quiz_name} - {self.score}"


#MCQ based
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

    # question = models.ForeignKey(
    #     McqQuestions,
    #     on_delete=models.CASCADE,
    #     # null=True,
    #     blank=True,
    #     related_name='quiz_reference'
    # )

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
    user = models.ForeignKey(MedicalHealthUser, on_delete=models.CASCADE)
    quiz = models.ForeignKey(McqQuiz, on_delete=models.CASCADE)
    score = models.PositiveIntegerField()
    total_questions = models.PositiveIntegerField()
    skip_questions = models.PositiveIntegerField(default=0)  
    performance = models.CharField(max_length=50, blank=True, null=True)  # e.g., "Excellent", "Good", "Average", "Poor",
    percentage = models.FloatField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name} - {self.quiz.name} - {self.score}/{self.total_questions}"
    


# for treatment models
class Steps(models.Model):
    step_1 = models.JSONField(null=True, blank=True, default=dict)
    step_2 = models.JSONField(null=True, blank=True, default=dict)
    step_3 = models.JSONField(null=True, blank=True, default=dict)
    step_4 = models.JSONField(null=True, blank=True, default=dict)
    step_5 = models.JSONField(null=True, blank=True, default=dict)
    step_6 = models.JSONField(null=True, blank=True, default=dict)
    step_7 = models.JSONField(null=True, blank=True, default=dict)
    step_8 = models.JSONField(null=True, blank=True, default=dict)
    step_9 = models.JSONField(null=True, blank=True, default=dict)
    step_10 = models.JSONField(null=True, blank=True, default=dict)

    type = models.CharField(max_length=10, choices=[("increase", "Increase"), ("decrease", "Decrease")], null=True, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='steps',
        null=True, blank=True
    )
    
    def __str__(self):
        return f"Steps for Category: {self.category.category} - Type: {self.type}"
    

class Treatment(models.Model):
    INCREASE = "increase"
    DECREASE = "decrease"
    TREATMENT_TYPE_CHOICES = [
        (INCREASE, "Increase"),
        (DECREASE, "Decrease"),
    ]

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="treatments"
    )
    user = models.ForeignKey(
        MedicalHealthUser,
        on_delete=models.CASCADE,
        related_name="treatments"
    )
    steps = models.ForeignKey(
        Steps,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="treatments"
    )
    type = models.CharField(
        max_length=10,
        choices=TREATMENT_TYPE_CHOICES
    )

    current_step = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Index (1-10) of step user is currently on."
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"Treatment #{self.id} • {self.user} • "
            f"{self.category.category} • {self.type} • "
            f"Step {self.current_step}"
        )


class Feedback(models.Model):
    treatment = models.ForeignKey(Treatment, on_delete=models.CASCADE)
    user = models.ForeignKey(MedicalHealthUser, on_delete=models.CASCADE)
    description = models.JSONField()          # Django ≥3.1

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Feedback"
        # optional uniqueness constraint:
        # unique_together = ("treatment", "user")

    def __str__(self):
        return f"Feedback #{self.id} by {self.user} on Treatment {self.treatment_id}"
