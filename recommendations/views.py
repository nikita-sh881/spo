# recommendations/views.py
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from .services import RecommendationService
from .serializers import RecommendationSerializer, BookLinkSerializer
from .models import BookLink
from books.models import Book
from books.serializers import BookSerializer

class RecommendationViewSet(GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'], url_path='for-me')
    def for_me(self, request):
        """
        Получить персональные рекомендации для текущего пользователя
        """
        recommendations = RecommendationService.get_recommendations_for_user(
            request.user.id,
            limit=request.query_params.get('limit', 10)
        )
        
        result = []
        for rec in recommendations:
            result.append({
                'book': BookSerializer(rec['book']).data,
                'reason': rec['reason'],
                'score': rec['score']
            })
        
        return Response({
            'count': len(result),
            'recommendations': result
        })
    
    @action(detail=False, methods=['get'], url_path='similar-to/(?P<book_id>[^/.]+)')
    def similar_to(self, request, book_id=None):
        """
        Получить похожие книги (для блока "Читатели также брали")
        """
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return Response({'error': 'Книга не найдена'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        similar_books = RecommendationService.get_similar_books(book_id, limit=6)
        serializer = BookSerializer(similar_books, many=True)
        
        return Response({
            'book': BookSerializer(book).data,
            'similar_books': serializer.data
        })
    
    class BookLinkViewSet(GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BookLinkSerializer
    
    def get_queryset(self):
        return BookLink.objects.filter(is_active=True)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def create_link(self, request):
        """
        Создание ручной связи между книгами (только для сотрудников)
        """
        if request.user.role not in ['librarian', 'admin']:
            return Response({'error': 'Доступ только для сотрудников'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        source_book_id = request.data.get('source_book_id')
        target_book_id = request.data.get('target_book_id')
        link_type = request.data.get('link_type')
        
        if not all([source_book_id, target_book_id, link_type]):
            return Response({'error': 'Необходимы source_book_id, target_book_id, link_type'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        link, created = BookLink.objects.get_or_create(
            source_book_id=source_book_id,
            target_book_id=target_book_id,
            defaults={
                'link_type': link_type,
                'created_by': request.user,
                'is_active': True
            }
        )
        
        if not created:
            link.link_type = link_type
            link.save()
        
        return Response(BookLinkSerializer(link).data, 
                       status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['delete'])
    def delete_link(self, request, pk=None):
        """Удаление связи (деактивация)"""
        if request.user.role not in ['librarian', 'admin']:
            return Response({'error': 'Доступ только для сотрудников'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        try:
            link = BookLink.objects.get(id=pk)
            link.is_active = False
            link.save()
            return Response({'status': 'deleted'})
        except BookLink.DoesNotExist:
            return Response({'error': 'Связь не найдена'}, 
                          status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'], url_path='for-book/(?P<book_id>[^/.]+)')
    def for_book(self, request, book_id=None):
        """
        Получить все исходящие связи для конкретной книги
        """
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return Response({'error': 'Книга не найдена'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        links = BookLink.objects.filter(
            source_book=book,
            is_active=True
        ).select_related('target_book')
        
        result = []
        for link in links:
            result.append({
                'id': link.id,
                'target_book': BookSerializer(link.target_book).data,
                'link_type': link.link_type,
                'link_type_display': link.get_link_type_display()
            })
        
        return Response(result)