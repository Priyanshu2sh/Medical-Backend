from django.db import models
from accounts.models import User


# Create your models here.
class CounsellorRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='client_sessions',
    )
    counsellor = models.ForeignKey(
        User,  # Not CounsellorProfile!
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
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Counsellor Session"
        verbose_name_plural = "Counsellor Sessions"
        ordering = ['-created_at']

    def __str__(self):
        return f"Session #{self.id} - {self.user} with {self.counsellor}"