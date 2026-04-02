"""
URL configuration for smartlib project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="SmartLib API",
        default_version='v1',
        description="Библиотечное веб-приложение",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

from users.views import RegisterView, ProfileView, CustomTokenObtainPairView
from books.views import BookViewSet, GenreViewSet
from circulation.views import IssuanceViewSet
from recommendations.views import RecommendationViewSet, BookLinkViewSet

router = routers.DefaultRouter()
router.register(r'books', BookViewSet)
router.register(r'genres', GenreViewSet)
router.register(r'issuances', IssuanceViewSet)
router.register(r'recommendations', RecommendationViewSet, basename='recommendations')
router.register(r'book-links', BookLinkViewSet, basename='book-links')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/', include(router.urls)),
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/profile/', ProfileView.as_view(), name='profile'),
    
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
