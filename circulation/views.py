from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Issuance
from .serializers import IssuanceSerializer, IssuanceCreateSerializer
from books.models import BookCopy
from users.models import User

class IssuanceViewSet(viewsets.ModelViewSet):
    serializer_class = IssuanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['librarian', 'admin']:
            return Issuance.objects.all().select_related('user', 'book_copy__book')
        return Issuance.objects.filter(user=user).select_related('book_copy__book')
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def issue(self, request):
        """Оформление выдачи (только для сотрудников)"""
        if request.user.role not in ['librarian', 'admin']:
            return Response({'error': 'Доступ только для сотрудников'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        serializer = IssuanceCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            book_copy = BookCopy.objects.get(id=serializer.validated_data['book_copy_id'])
            user = User.objects.get(id=serializer.validated_data['user_id'])
        except (BookCopy.DoesNotExist, User.DoesNotExist):
            return Response({'error': 'Книга или пользователь не найдены'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        if book_copy.status != 'available':
            return Response({'error': 'Книга недоступна для выдачи'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        due_date = serializer.validated_data.get('due_date')
        if not due_date:
            days = 14 + (book_copy.book.pages // 100)
            due_date = timezone.now() + timezone.timedelta(days=days)

        issuance = Issuance.objects.create(
            book_copy=book_copy,
            user=user,
            due_date=due_date
        )

        book_copy.status = 'issued'
        book_copy.save()
        
        book = book_copy.book
        book.available_copies -= 1
        book.times_issued_total += 1
        book.last_issued_date = timezone.now()
        book.save()
        
        user.books_taken_total += 1
        user.save()
        
        return Response(IssuanceSerializer(issuance).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def return_book(self, request, pk=None):
        """Оформление возврата"""
        if request.user.role not in ['librarian', 'admin']:
            return Response({'error': 'Доступ только для сотрудников'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        try:
            issuance = Issuance.objects.get(id=pk, returned_date__isnull=True)
        except Issuance.DoesNotExist:
            return Response({'error': 'Выдача не найдена или уже возвращена'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        issuance.returned_date = timezone.now()
        
        if issuance.returned_date > issuance.due_date:
            issuance.is_returned_on_time = False
            issuance.days_overdue = (issuance.returned_date - issuance.due_date).days
        
        issuance.save()
  
        book_copy = issuance.book_copy
        book_copy.status = 'available'
        book_copy.save()
        
        book = book_copy.book
        book.available_copies += 1
        book.save()
        
        return Response(IssuanceSerializer(issuance).data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Список просроченных выдач (только для сотрудников)"""
        if request.user.role not in ['librarian', 'admin']:
            return Response({'error': 'Доступ только для сотрудников'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        overdue = Issuance.objects.filter(
            returned_date__isnull=True,
            due_date__lt=timezone.now()
        ).select_related('user', 'book_copy__book')
        
        serializer = self.get_serializer(overdue, many=True)
        return Response(serializer.data)