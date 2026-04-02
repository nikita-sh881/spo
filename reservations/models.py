from django.db import models
from django.conf import settings
from books.models import Book

class Reservation(models.Model):
    STATUS_CHOICES = (
        ('waiting', 'В очереди'),
        ('ready', 'Готова к выдаче'),
        ('completed', 'Выдана'),
        ('expired', 'Просрочена'),
    )
    
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reservations')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reservations')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    queue_position = models.IntegerField()
    
    class Meta:
        ordering = ['queue_position']
    
    def __str__(self):
        return f"{self.book.title} - {self.user.username} ({self.status})"
