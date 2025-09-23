from django.db import models
from assessments.models import MedicalHealthUser


# Create your models here.
class CounsellorRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(
        MedicalHealthUser, 
        on_delete=models.CASCADE,
        related_name='client_sessions',
    )
    counsellor = models.ForeignKey(
        MedicalHealthUser,  # Not CounsellorProfile!
        on_delete=models.CASCADE,
        related_name='counsellor_sessions',
        limit_choices_to={'role': 'Counsellor'},  # Ensures only counsellors can be selected
        
    )
    description = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    rq_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Counsellor Session"
        verbose_name_plural = "Counsellor Sessions"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # First save to get the PK
        if not self.rq_id:
            self.rq_id = f"{self.pk:07d}"  # Format the ID as 0000001
            # Save again to update RQ field
            CounsellorRequest.objects.filter(pk=self.pk).update(rq_id=self.rq_id)

    def __str__(self):
        return f"Session #{self.rq_id} - {self.user} with {self.counsellor}"


class Precaution(models.Model):
    description = models.TextField()

    def __str__(self):
        return self.description[:50]  # Show first 50 chars

class TherapySteps(models.Model):
    trm_id = models.CharField(max_length=10, unique=True, null=True, blank=True)
    therapy_title = models.CharField(max_length=255, null=True, blank=True)
    request_id = models.ForeignKey(
        'CounsellorRequest',
        on_delete=models.CASCADE,
        related_name='therapies',
        null=True,
        blank=True
    )
    counsellor = models.ForeignKey(
        MedicalHealthUser,
        on_delete=models.CASCADE,
        related_name='therapy_given',
        limit_choices_to={'role': 'Counsellor'}
    )
    user = models.ForeignKey(
        MedicalHealthUser,
        on_delete=models.CASCADE,
        related_name='therapy_received'
    )

    # Steps
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

    current_step = models.PositiveIntegerField(default=1)
    
    precautions = models.ManyToManyField(Precaution, related_name='therapies')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Therapy Step"
        verbose_name_plural = "Therapy Steps"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.trm_id:
            self.trm_id = f"{self.pk:07d}"  # Format like 0000001
            TherapySteps.objects.filter(pk=self.pk).update(trm_id=self.trm_id)

    def __str__(self):
        return f"Therapy {self.trm_id} for {self.user.username}"
    

class Feedback(models.Model):
    therapy_steps = models.ForeignKey(
        'TherapySteps',
        on_delete=models.CASCADE,
        related_name='feedbacks'
    )
    user = models.ForeignKey(
        MedicalHealthUser,
        on_delete=models.CASCADE,
        related_name='feedbacks'
    )
    description = models.JSONField(default=dict)  # Holds step-wise feedback
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Feedback by {self.user.username} for {self.therapy_steps.therapy_steps}"