from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'roles', RoleViewSet)
router.register(r'users', UserViewSet)
router.register(r'albums', AlbumViewSet)
router.register(r'genres', GenreViewSet)
router.register(r'songs', SongViewSet)
router.register(r'playlists', PlaylistViewSet)



urlpatterns = [
    path('', include(router.urls)),
    # path('register/', RegisterView.as_view(), name='register'),
    # path('login/', LoginView.as_view(), name='login'),
]

