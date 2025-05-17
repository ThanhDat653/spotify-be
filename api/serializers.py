from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Role, User, Genre, Song, Album, Playlist


# === BASIC SERIALIZERS (for nested usage) ===

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']


class UserPublicSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    avatar = serializers.ImageField(use_url=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'avatar', 'role', 'fullname']



class AlbumMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = ['id', 'title']

class ArtistMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'fullname']

class SongMiniSerializer(serializers.ModelSerializer):
    artist = serializers.SerializerMethodField()
    url = serializers.FileField(use_url=False)
    thumbnail = serializers.ImageField(use_url=False)

    class Meta:
        model = Song
        fields = ['id', 'title', 'duration', 'artist', 'url', 'thumbnail']

    def get_artist(self, obj):
        return [{'id': artist.id, 'name': artist.fullname} for artist in obj.artists.all()]


# === MAIN SERIALIZERS ===

class ArtistSerializer(serializers.ModelSerializer):
    songs = serializers.SerializerMethodField()
    albums = serializers.SerializerMethodField()
    avatar = serializers.ImageField(use_url=False)


    class Meta:
        model = User
        fields = ['id', 'avatar', 'username', 'fullname', 'albums', 'songs']

    def get_songs(self, obj):
        return SongSerializer(obj.songs.all(), many=True).data

    def get_albums(self, obj):
        return AlbumSerializer(Album.objects.filter(creator=obj), many=True).data


class UserSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(), write_only=True, source='role'
    )
    avatar = serializers.ImageField(use_url=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'fullname', 'email', 'password', 'avatar', 'createAt', 'role', 'role_id']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)
        instance.save()
        return instance


class AlbumSerializer(serializers.ModelSerializer):
    creator = UserPublicSerializer(read_only=True)
    creator_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='creator'
    )
    poster = serializers.ImageField(use_url=False)

    songs = SongMiniSerializer(many=True, read_only=True)

    class Meta:
        model = Album
        fields = ['id', 'title', 'releaseDate', 'poster', 'creator', 'creator_id', 'songs']


class SongSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    genre_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Genre.objects.all(), write_only=True, source='genre'
    )

    url = serializers.FileField(use_url=False)
    thumbnail = serializers.ImageField(use_url=False)

    albums = AlbumMiniSerializer(many=True, read_only=True)
    albums_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Album.objects.all(), write_only=True, source='albums'
    )

    artists = UserPublicSerializer(many=True, read_only=True)
    artists_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), write_only=True, source='artists'
    )

    class Meta:
        model = Song
        fields = [
            'id', 'title', 'duration', 'url', 'thumbnail',
            'genre', 'genre_ids',
            'albums', 'albums_ids',
            'artists', 'artists_ids'
        ]


class PlaylistSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='user'
    )

    songs = SongMiniSerializer(many=True, read_only=True)
    song_id = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Song.objects.all(), write_only=True, source='songs'
    )

    poster = serializers.ImageField(use_url=False)

    class Meta:
        model = Playlist
        fields = ['id', 'name', 'createAt', 'poster', 'user', 'user_id', 'songs', 'song_id']

# === AUTH SERIALIZERS ===

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'role', 'avatar', 'fullname')
        extra_kwargs = {
            'password': {'write_only': True},
            'avatar': {'required': False}
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return User.objects.create(**validated_data)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    token = serializers.CharField(read_only=True)
    user = UserPublicSerializer(read_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")
        user = authenticate(username=username, password=password)

        if user and user.is_active:
            refresh = RefreshToken.for_user(user)
            return {
                'token': str(refresh.access_token),
                'user': UserPublicSerializer(user).data
            }

        raise serializers.ValidationError("Invalid credentials")
