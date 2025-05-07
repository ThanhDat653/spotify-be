from django.contrib import admin
from .models import Role, User, Album, Genre, Song, Playlist

admin.site.register(Role)
admin.site.register(User)
admin.site.register(Album)
admin.site.register(Genre)
admin.site.register(Song)
admin.site.register(Playlist)
