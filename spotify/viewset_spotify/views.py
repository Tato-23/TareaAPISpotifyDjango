from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import SpotifyUser, SpotifyPreference
from .serializer import SpotifyUserSerializer, SpotifyPreferenceSerializer
from .service.spotify import get_auth_url, get_spotify_token, get_user_profile, get_top_tracks

class SpotifyAuthViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['get'], url_path='login')
    def auth_url(self, request):
        url = get_auth_url()
        return Response({'auth_url': url}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='callback')
    def callback(self,request):
        try:
            token_info = get_spotify_token()
            return Response(token_info, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=['get'], url_path='profile')
    def user_profile(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return Response({'error': 'El token de autorización es requerido.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            access_token = auth_header.replace('Bearer ', '')
            profile = get_user_profile(access_token)
            return Response(profile, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class SpotifyUserViewSet(viewsets.ModelViewSet):
    queryset = SpotifyUser.objects.all().order_by('-created_at')
    serializer_class = SpotifyUserSerializer
    lookup_field = 'spotify_id'
    http_method_names = ['get', 'post', 'put','patch', 'delete']

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({'message': 'No hay usuarios de Spotify registrados.'}, status=status.HTTP_200_OK)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        user_profile = get_user_profile(request.data.get('access_token', ''))

        if 'error' in user_profile:
            return Response({'error': 'Token de acceso inválido o expirado.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            request.data['spotify_id'] = user_profile.get('id')
            request.data['email'] = user_profile.get('email')
            request.data['nombre'] = user_profile.get('display_name')
            request.data['country'] = user_profile.get('country')

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['put'], url_path='update-user')
    def update_user(self, request):
        spotify_id = request.query_params.get('spotify_id')
        if not spotify_id:
            return Response({'error': 'El spotify_id es requerido.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = self.get_queryset().get(spotify_id=spotify_id)
        except SpotifyUser.DoesNotExist:
            return Response({'error': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(user, data=request.data)
        
        # Comparar initial_data con los datos actuales del usuario
        datos_iguales = all(
            getattr(user, campo, None) == valor 
            for campo, valor in serializer.initial_data.items() 
            if hasattr(user, campo)
        )
        
        if datos_iguales and serializer.initial_data:
            return Response({'message': 'El usuario ya existe con estos datos.'}, status=status.HTTP_200_OK)

        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({'message': 'Usuario actualizado correctamente', 'data': serializer.data}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['delete'], url_path='delete-user')
    def delete_user(self, request):
        spotify_id = request.query_params.get('spotify_id')
        if not spotify_id:
            return Response({'error': 'El spotify_id es requerido.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = self.get_queryset().get(spotify_id=spotify_id)
            user.delete()
            return Response({'message': 'Usuario eliminado correctamente.'}, status=status.HTTP_200_OK)
        except SpotifyUser.DoesNotExist:
            return Response({'error': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        

class SpotifyPreferenceViewSet(viewsets.ModelViewSet):
    queryset = SpotifyPreference.objects.all()
    serializer_class = SpotifyPreferenceSerializer
    lookup_field = 'spotify_id'
    http_method_names = ['get', 'post', 'put', 'delete']

    #Obtener preferencias de Spotify desde API
    @action(detail=False, methods=['get'], url_path='preferences-top-tracks')
    def preferences_by_user(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return Response({'error': 'El token de autorización es requerido.'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            access_token = auth_header.replace('Bearer ', '')
            top_tracks = get_top_tracks(access_token)
            if not top_tracks or 'items' not in top_tracks:
                return Response({'error': 'No se pudieron obtener las pistas principales.'}, status=status.HTTP_400_BAD_REQUEST)
            preferences = []
            for item in top_tracks['items']:
                preference_data = {
                    'track_name': item['name'],
                    'artist_name': ', '.join(artist['name'] for artist in item['artists']),
                }
                preferences.append(preference_data)
            return Response(preferences, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


    # Listar preferencias de Spotify desde BD
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({'message': 'No hay preferencias de Spotify registradas.'}, status=status.HTTP_200_OK)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    # Crear preferencia de Spotify en BD
    def create(self, request, *args, **kwargs):
        # Obtener datos del request
        access_token = request.data.get('access_token', '')
        spotify_id = request.data.get('spotify_id', '')

        # Validar que se proporcione el spotify_id
        if not spotify_id:
            return Response({'error': 'El spotify_id es requerido.'}, status=status.HTTP_400_BAD_REQUEST)

        # Obtener preferencias de Spotify
        preference = get_top_tracks(access_token)

        if 'error' in preference:
            return Response({'error': 'Token de acceso inválido o expirado.'}, status=status.HTTP_400_BAD_REQUEST)
        
        items = preference.get('items', [])
        if not items:
            return Response({'error': 'No se encontraron preferencias musicales.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Guardar todas las preferencias musicales
        created_preferences = []
        errors = []
        
        for track in items:
            data = {
                'spotify_id': spotify_id,
                'track_name': track.get('name'),
                'artist_name': ', '.join(artist['name'] for artist in track.get('artists', []))
            }
            
            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                self.perform_create(serializer)
                created_preferences.append(serializer.data)
            else:
                # Si el track ya existe, lo omitimos pero continuamos
                errors.append({
                    'track_name': data['track_name'],
                    'error': "El track ya existe o hubo un error de validación."
                })
        
        if not created_preferences and errors:
            return Response({
                'message': 'No se pudieron crear las preferencias.',
                'errors': errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'message': f'Se crearon {len(created_preferences)} preferencias musicales.',
            'preferencias': created_preferences,
        }, status=status.HTTP_201_CREATED)
    
            

        



    
        
    