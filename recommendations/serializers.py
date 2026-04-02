from rest_framework import serializers
from .models import BookLink
from books.serializers import BookSerializer

class BookLinkSerializer(serializers.ModelSerializer):
    source_book_title = serializers.CharField(source='source_book.title', read_only=True)
    target_book_title = serializers.CharField(source='target_book.title', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    link_type_display = serializers.CharField(source='get_link_type_display', read_only=True)
    
    class Meta:
        model = BookLink
        fields = ['id', 'source_book', 'source_book_title', 'target_book', 
                  'target_book_title', 'link_type', 'link_type_display',
                  'created_by', 'created_by_name', 'created_at', 'weight', 'is_active']
        read_only_fields = ['id', 'created_at', 'created_by']

class RecommendationSerializer(serializers.Serializer):
    book = BookSerializer()
    reason = serializers.CharField()
    score = serializers.IntegerField()