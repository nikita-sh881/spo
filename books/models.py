from django.db import models

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=300)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=20, unique=True, blank=True, null=True)
    publication_year = models.IntegerField()
    publisher = models.CharField(max_length=200, blank=True)
    pages = models.IntegerField(default=0)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    total_copies = models.IntegerField(default=1)
    available_copies = models.IntegerField(default=1)
    last_issued_date = models.DateTimeField(null=True, blank=True)
    times_issued_total = models.IntegerField(default=0)
    cover_image = models.ImageField(upload_to='covers/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.author}"

class BookCopy(models.Model):
    STATUS_CHOICES = (
        ('available', 'В библиотеке'),
        ('issued', 'Выдана'),
        ('reserved', 'Зарезервирована'),,
        ('lost', 'Потеряна'),
    )
    
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='copies')
    inventory_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    location = models.CharField(max_length=100, blank=True)
    added_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.book.title} (инв. {self.inventory_number})"
