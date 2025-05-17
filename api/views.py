import random
from rest_framework import viewsets, generics, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db.models import Prefetch

from .models import Role, User, Genre, Song, Album, Playlist
from .serializers import (
    RoleSerializer, UserSerializer, GenreSerializer,
    SongSerializer, AlbumSerializer, PlaylistSerializer,
    RegisterSerializer, LoginSerializer, UserPublicSerializer, ArtistSerializer
)


# ======= VIEWSETS =======

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class ArtistViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(role__id=1)
    serializer_class = ArtistSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'fullname']

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'fullname']


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class SongViewSet(viewsets.ModelViewSet):
    queryset = Song.objects.all()
    serializer_class = SongSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'albums__title', 'artists__fullname', 'genre__name'], 
    ordering_fields = ['title']
    
    @action(detail=True, methods=['post'], url_path='increase-play')
    def increase_play(self, request, pk=None):
        song = self.get_object()
        song.play_count += 1
        song.save()
        return Response({'message': 'Play count increased'}, status=status.HTTP_200_OK)


class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    
    @action(detail=True, methods=['post'], url_path='add-song')
    def add_song(self, request, pk=None):
        album = self.get_object()
        song_id = request.data.get('song_id')

        if not song_id:
            return Response({'error': 'Missing song_id'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            song = Song.objects.get(pk=song_id)
        except Song.DoesNotExist:
            return Response({'error': 'Song not found'}, status=status.HTTP_404_NOT_FOUND)

        album.songs.add(song)
        return Response({'message': 'Song added successfully'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], url_path='remove-song')
    def remove_song(self, request, pk=None):
        album = self.get_object()
        song_id = request.data.get('song_id')

        if not song_id:
            return Response({'error': 'Missing song_id'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            song = Song.objects.get(pk=song_id)
        except Song.DoesNotExist:
            return Response({'error': 'Song not found'}, status=status.HTTP_404_NOT_FOUND)

        if song not in album.songs.all():
            return Response({'error': 'Song not in album'}, status=status.HTTP_400_BAD_REQUEST)

        album.songs.remove(song)
        return Response({'message': 'Song removed successfully'}, status=status.HTTP_200_OK)


class PlaylistViewSet(viewsets.ModelViewSet):
    queryset = Playlist.objects.all()
    serializer_class = PlaylistSerializer
    
    @action(detail=True, methods=['post'], url_path='add-song')
    def add_song(self, request, pk=None):
        playlist = self.get_object()
        song_id = request.data.get('song_id')

        if not song_id:
            return Response({'error': 'Missing song_id'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            song = Song.objects.get(pk=song_id)
        except Song.DoesNotExist:
            return Response({'error': 'Song not found'}, status=status.HTTP_404_NOT_FOUND)

        playlist.songs.add(song)
        return Response({'message': 'Song added successfully'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], url_path='remove-song')
    def remove_song(self, request, pk=None):
        playlist = self.get_object()
        song_id = request.data.get('song_id')

        if not song_id:
            return Response({'error': 'Missing song_id'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            song = Song.objects.get(pk=song_id)
        except Song.DoesNotExist:
            return Response({'error': 'Song not found'}, status=status.HTTP_404_NOT_FOUND)

        if song not in playlist.songs.all():
            return Response({'error': 'Song not in playlist'}, status=status.HTTP_400_BAD_REQUEST)

        playlist.songs.remove(song)
        return Response({'message': 'Song removed successfully'}, status=status.HTTP_200_OK)


# ======= AUTH & REGISTER =======

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)


# ======= GET CURRENT USER (ME) =======

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserPublicSerializer(request.user).data)

# ======= GET LANGING PLAYLIST =======

class LandingPageAPIView(APIView):
    def get(self, request):
        genres = Genre.objects.prefetch_related('song_set')

        playlists_by_genre = []
        for genre in genres:
            songs = genre.song_set.all()[:10]  # Slice an toàn sau khi prefetch
            playlists_by_genre.append({
                "genre": genre.name,
                "songs": SongSerializer(songs, many=True).data
            })

        top_trending_songs = Song.objects.order_by('-play_count')[:10]

        all_album_ids = list(Album.objects.values_list('id', flat=True))
        random_ids = random.sample(all_album_ids, min(len(all_album_ids), 5))
        random_albums = Album.objects.filter(id__in=random_ids)

        return Response({
            "playlists_by_genre": playlists_by_genre,
            "top_trending_songs": SongSerializer(top_trending_songs, many=True).data,
            "random_albums": AlbumSerializer(random_albums, many=True).data
        }, status=status.HTTP_200_OK)
