from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .serializers import ArtistSerializer
from .views import *

router = DefaultRouter()
router.register(r'roles', RoleViewSet)
router.register(r'users', UserViewSet)
router.register(r'genres', GenreViewSet)
router.register(r'songs', SongViewSet)
router.register(r'albums', AlbumViewSet)
router.register(r'playlists', PlaylistViewSet)
router.register(r'artists', ArtistViewSet, basename='artist')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', RegisterView.as_view()),
    path('auth/login/', LoginView.as_view()),
    path('auth/me/', MeView.as_view()),
]
