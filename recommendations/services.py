from django.db.models import Count, Q
from books.models import Book, BookCopy
from circulation.models import Issuance
from users.models import User

class RecommendationService:
    
    @staticmethod
    def get_recommendations_for_user(user_id, limit=10):
        """
        Персональные рекомендации на основе истории чтения
        """
        user = User.objects.get(id=user_id)
        
        history = Issuance.objects.filter(
            user=user,
            returned_date__isnull=False
        ).select_related('book_copy__book__genre').order_by('-issued_date')[:20]
        
        if not history:
            return RecommendationService._get_popular_books(limit)

        author_count = {}
        genre_count = {}
        
        for issuance in history:
            book = issuance.book_copy.book
            author_count[book.author] = author_count.get(book.author, 0) + 1
            if book.genre:
                genre_count[book.genre.id] = genre_count.get(book.genre.id, 0) + 1
        

        top_authors = sorted(author_count.items(), key=lambda x: x[1], reverse=True)[:3]
        top_genres = sorted(genre_count.items(), key=lambda x: x[1], reverse=True)[:3]
        

        from recommendations.models import UserPreference
        UserPreference.objects.update_or_create(
            user=user,
            defaults={
                'top_authors': dict(top_authors),
                'top_genres': dict(top_genres)
            }
        )

        taken_book_ids = Issuance.objects.filter(user=user).values_list('book_copy__book_id', flat=True).distinct()
        
        recommendations = []

        for author, _ in top_authors:
            books = Book.objects.filter(
                author=author,
                total_copies__gt=0
            ).exclude(
                id__in=taken_book_ids
            ).select_related('genre')[:3]
            
            for book in books:
                recommendations.append({
                    'book': book,
                    'reason': f'Вам нравятся книги автора {author}',
                    'score': 10
                })

        for genre_id, _ in top_genres:
            from books.models import Genre
            genre = Genre.objects.get(id=genre_id)
            
            books = Book.objects.filter(
                genre=genre
            ).exclude(
                id__in=taken_book_ids
            ).exclude(
                author__in=[a for a, _ in top_authors]
            ).select_related('genre')[:3]
            
            for book in books:
                recommendations.append({
                    'book': book,
                    'reason': f'Вы любите жанр {genre.name}',
                    'score': 8
                })

        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec['book'].id not in seen:
                seen.add(rec['book'].id)
                unique_recommendations.append(rec)

        unique_recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return unique_recommendations[:limit]
    
    @staticmethod
    def _get_popular_books(limit):
        """Популярные книги (если нет истории)"""
        popular_books = Book.objects.filter(
            total_copies__gt=0
        ).order_by('-times_issued_total')[:limit]
        
        return [{'book': book, 'reason': 'Популярная книга', 'score': 5} 
                for book in popular_books]
    
    @staticmethod
    def get_similar_books(book_id, limit=6):
        """
        Похожие книги для блока "Читатели также брали"
        """
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return []

        users_who_took = Issuance.objects.filter(
            book_copy__book=book,
            returned_date__isnull=False
        ).values_list('user_id', flat=True).distinct()
        
        similar_books = Book.objects.filter(
            copies__issuances__user_id__in=users_who_took
        ).exclude(
            id=book_id
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:limit]
        
        if similar_books.count() < limit:
            remaining = limit - similar_books.count()
            by_author = Book.objects.filter(
                author=book.author
            ).exclude(
                id=book_id
            ).exclude(
                id__in=[b.id for b in similar_books]
            )[:remaining]
            
            similar_books = list(similar_books) + list(by_author)
        
        return similar_books