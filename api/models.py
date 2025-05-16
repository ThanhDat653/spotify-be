from django.db import models

class Role(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100)
    email = models.CharField(max_length=100, null=True)
    password = models.CharField(max_length=100)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    createAt = models.DateField(auto_now_add=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.role.name} - {self.username}"

class Genre(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Song(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    duration = models.IntegerField()
    genre = models.ManyToManyField(Genre,blank=True)
    url = models.FileField(upload_to='songs/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', null=True, blank=True)  # ✅ ảnh thumbnail
    albums = models.ManyToManyField('Album', related_name='songs')
    artists = models.ManyToManyField(User, related_name='songs')

    def __str__(self):
        return self.title

class Album(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    releaseDate = models.DateField(auto_now_add=True)
    poster = models.ImageField(upload_to='posters/', null=True, blank=True)  # ✅ ảnh poster
    creator = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Playlist(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    createAt = models.DateField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    poster = models.ImageField(upload_to='posters/', null=True, blank=True)  # ✅ ảnh poster
    songs = models.ManyToManyField(Song)

    def __str__(self):
        return self.name
