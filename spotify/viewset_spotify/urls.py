from rest_framework.routers import DefaultRouter
from .views import SpotifyAuthViewSet, SpotifyUserViewSet, SpotifyPreferenceViewSet

router = DefaultRouter()
router.register(r'spotify-auth', SpotifyAuthViewSet, basename='spotify-auth')
router.register(r'spotify-users', SpotifyUserViewSet, basename='spotify-users')
router.register(r'spotify-preferences', SpotifyPreferenceViewSet, basename='spotify-preferences')

urlpatterns = router.urls