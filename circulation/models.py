from django.db import models
from django.conf import settings
from books.models import BookCopy

class Issuance(models.Model):
    book_copy = models.ForeignKey(BookCopy, on_delete=models.CASCADE, related_name='issuances')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='issuances')
    issued_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    returned_date = models.DateTimeField(null=True, blank=True)
    is_returned_on_time = models.BooleanField(default=True)
    days_overdue = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.book_copy.book.title} -> {self.user.username} ({self.issued_date.date()})"
