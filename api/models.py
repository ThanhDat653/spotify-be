from django.db import models

class Role(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    createAt = models.DateField(auto_now_add=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

class Album(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    releaseDate = models.DateField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Genre(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

class Song(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    duration = models.IntegerField()
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    url = models.CharField(max_length=200, default='/mp4')

class Playlist(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    createAt = models.DateField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    songs = models.ManyToManyField(Song)
