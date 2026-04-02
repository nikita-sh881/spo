from rest_framework import viewsets, filters, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .models import Book, Genre
from .serializers import BookSerializer, GenreSerializer
from .permissions import IsLibrarianOrAdmin 

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all().select_related('genre').prefetch_related('copies')
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['genre', 'author', 'publication_year']
    search_fields = ['title', 'author', 'isbn']
    ordering_fields = ['title', 'author', 'publication_year', 'times_issued_total']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsLibrarianOrAdmin()]
        return [permissions.AllowAny()]

class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [permissions.AllowAny]