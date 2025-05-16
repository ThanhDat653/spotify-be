from rest_framework import viewsets, generics, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

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
    search_fields = ['username']

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    search_fields = ['username']


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class SongViewSet(viewsets.ModelViewSet):
    queryset = Song.objects.all()
    serializer_class = SongSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'albums__title', 'artists__username']


class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer


class PlaylistViewSet(viewsets.ModelViewSet):
    queryset = Playlist.objects.all()
    serializer_class = PlaylistSerializer


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
