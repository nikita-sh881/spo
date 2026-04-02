from rest_framework import serializers
from .models import Issuance
from books.serializers import BookSerializer

class IssuanceSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book_copy.book.title', read_only=True)
    book_author = serializers.CharField(source='book_copy.book.author', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Issuance
        fields = ['id', 'book_copy', 'book_title', 'book_author', 'user', 'user_name',
                  'issued_date', 'due_date', 'returned_date', 'is_returned_on_time', 'days_overdue']
        read_only_fields = ['id', 'issued_date', 'is_returned_on_time', 'days_overdue']

class IssuanceCreateSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    book_copy_id = serializers.IntegerField()
    due_date = serializers.DateTimeField(required=False)