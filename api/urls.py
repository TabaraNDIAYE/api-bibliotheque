# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    AuteurViewSet, LivreViewSet, TagViewSet, 
    EmpruntViewSet, ProfilViewSet, UserViewSet
)

router = DefaultRouter()
router.register(r'auteurs', AuteurViewSet, basename='auteur')
router.register(r'livres', LivreViewSet, basename='livre')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'emprunts', EmpruntViewSet, basename='emprunt')
router.register(r'profil', ProfilViewSet, basename='profil')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]