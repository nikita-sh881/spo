from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('reader', 'Читатель'),
        ('librarian', 'Сотрудник'),
        ('admin', 'Администратор'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='reader')
    phone = models.CharField(max_length=20, blank=True)
    library_card_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    is_blocked = models.BooleanField(default=False)
    books_taken_total = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"


