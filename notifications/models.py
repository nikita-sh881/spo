from django.db import models
from django.conf import settings
from books.models import Book

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('due_soon', 'Скоро сдавать'),
        ('overdue', 'Просрочка'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    related_book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username}: {self.title}"