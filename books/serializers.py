from rest_framework import serializers
from .models import Book, Genre, BookCopy

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name', 'description']

class BookCopySerializer(serializers.ModelSerializer):
    class Meta:
        model = BookCopy
        fields = ['id', 'inventory_number', 'status', 'location']

class BookSerializer(serializers.ModelSerializer):
    genre_name = serializers.CharField(source='genre.name', read_only=True)
    copies_status = serializers.SerializerMethodField()
    available_copies_display = serializers.IntegerField(source='available_copies', read_only=True)
    
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'isbn', 'publication_year', 
                  'publisher', 'pages', 'genre', 'genre_name', 'description',
                  'total_copies', 'available_copies_display', 'times_issued_total',
                  'cover_image', 'copies_status']
    
    def get_copies_status(self, obj):
        return [{'id': c.id, 'status': c.status, 'inventory_number': c.inventory_number} 
                for c in obj.copies.all()[:3]]