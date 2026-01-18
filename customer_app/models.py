from django.db import models
from django.utils.translation import gettext_lazy as _
from auth_app.models import User


class UserComment(models.Model):
    user = models.ForeignKey(
        User,
        related_name='comments',
        on_delete=models.CASCADE
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Comment by {self.user.email} on {self.created_at:%Y-%m-%d}"
