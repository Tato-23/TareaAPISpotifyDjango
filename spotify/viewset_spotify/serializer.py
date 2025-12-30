from rest_framework import serializers
from .models import SpotifyUser, SpotifyPreference

class SpotifyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpotifyUser
        fields = ['id', 'spotify_id', 'nombre', 'email', 'country', 'created_at', 'updated_at']
        read_only_fields = ['id','created_at', 'updated_at']
        extra_kwargs = {
            'email': {'allow_blank': True, 'required': False, 'validators': []},
            'nombre': {'allow_blank': True, 'required': False, 'validators': []},
            'spotify_id': {'allow_blank': True, 'required': False, 'validators': []},
        }

    # Validation to ensure unique fields
    def validate_spotify_id(self, value):
        if not value:
            raise serializers.ValidationError("El campo 'spotify_id' es obligatorio.")
        # Excluir el registro actual en updates
        qs = SpotifyUser.objects.filter(spotify_id=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Este Spotify ID ya existe.")
        return value
    
    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("El campo 'email' es obligatorio.")
        # Excluir el registro actual en updates
        qs = SpotifyUser.objects.filter(email=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Este email ya está registrado.")
        return value
    
    def validate_nombre(self, value):
        if not value:
            raise serializers.ValidationError("El campo 'nombre' es obligatorio.")
        # Excluir el registro actual en updates
        qs = SpotifyUser.objects.filter(nombre=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Este nombre ya está en uso.")
        return value
    

class SpotifyPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpotifyPreference
        fields = ['id', 'spotify_id', 'track_name', 'artist_name', 'created_at', 'updated_at']
        read_only_fields = ['id','created_at', 'updated_at']

        def validate_spotify_id(self, value):
            if SpotifyPreference.objects.filter(spotify_id=value).exists():
                raise serializers.ValidationError("Este Spotify ID ya existe en las preferencias.")
            return value