from django.db import models

class SpotifyUser(models.Model):
    spotify_id = models.CharField(max_length=255, unique=True)
    nombre = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre or self.spotify_id
    
class SpotifyPreference(models.Model):
    spotify_id = models.ForeignKey(SpotifyUser, to_field='spotify_id', on_delete=models.CASCADE, related_name='preferences')
    track_name = models.CharField(max_length=255, unique=True)
    artist_name = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Preferences of {self.user.nombre or self.user.spotify_id}"
    
class Meta:
    ordering = ['-created_at']