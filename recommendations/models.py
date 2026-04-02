from django.db import models
from django.conf import settings
from books.models import Book

class BookLink(models.Model):
    LINK_TYPES = (
        ('sequel', 'Продолжение'),
        ('prequel', 'Приквел'),
        ('same_author', 'Тот же автор'),
        ('same_genre', 'Тот же жанр'),
    )
    
    source_book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='outgoing_links')
    target_book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='incoming_links')
    link_type = models.CharField(max_length=20, choices=LINK_TYPES)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    weight = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['source_book', 'target_book']

class UserPreference(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='preferences')
    top_authors = models.JSONField(default=dict)
    top_genres = models.JSONField(default=dict)
    last_updated = models.DateTimeField(auto_now=True)