# api/views.py
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from .models import Auteur, Livre, Tag, Emprunt, ProfilLecteur
from .serializers import (
    AuteurSerializer, AuteurDetailSerializer, LivreSerializer, 
    LivreDetailSerializer, TagSerializer, EmpruntSerializer, 
    ProfilLecteurSerializer, UserSerializer
)
from .permissions import EstProprietaireOuReadOnly, EstProprietaireEmprunt
from .filters import LivreFilter
from .pagination import StandardPagination


class AuteurViewSet(viewsets.ModelViewSet):
    queryset = Auteur.objects.all()
    serializer_class = AuteurSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AuteurDetailSerializer
        return AuteurSerializer
    
    @action(detail=True, methods=['get'], url_path='livres')
    def livres(self, request, pk=None):
        auteur = self.get_object()
        livres = auteur.livres.all()
        serializer = LivreSerializer(livres, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        data = {
            'total_auteurs': Auteur.objects.count(),
            'total_livres': Livre.objects.count(),
            'nationalites': list(Auteur.objects.values_list('nationalite', flat=True).distinct()),
        }
        return Response(data)


class LivreViewSet(viewsets.ModelViewSet):
    queryset = Livre.objects.select_related('auteur').prefetch_related('tags').all()
    permission_classes = [EstProprietaireOuReadOnly]
    pagination_class = StandardPagination
    filterset_class = LivreFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['titre', 'auteur__nom', 'isbn']
    ordering_fields = ['titre', 'annee_publication', 'date_creation']
    ordering = ['-date_creation']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return LivreDetailSerializer
        return LivreSerializer
    
    def perform_create(self, serializer):
        serializer.save(cree_par=self.request.user)
    
    @action(detail=False, methods=['get'])
    def disponibles(self, request):
        queryset = self.get_queryset().filter(disponible=True)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def emprunter(self, request, pk=None):
        livre = self.get_object()
        if not livre.disponible:
            return Response(
                {'erreur': 'Ce livre n\'est pas disponible.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Créer un emprunt
        from datetime import date, timedelta
        Emprunt.objects.create(
            utilisateur=request.user,
            livre=livre,
            date_retour_prevue=date.today() + timedelta(days=14)
        )
        livre.disponible = False
        livre.save()
        return Response({'message': f'Livre "{livre.titre}" emprunté avec succès.'})
    
    @action(detail=True, methods=['post'])
    def rendre(self, request, pk=None):
        livre = self.get_object()
        emprunt = Emprunt.objects.filter(livre=livre, rendu=False).first()
        if emprunt:
            emprunt.rendu = True
            emprunt.save()
        livre.disponible = True
        livre.save()
        return Response({'message': f'Livre "{livre.titre}" rendu avec succès.'})


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class EmpruntViewSet(viewsets.ModelViewSet):
    serializer_class = EmpruntSerializer
    permission_classes = [IsAuthenticated, EstProprietaireEmprunt]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Emprunt.objects.all().select_related('livre', 'utilisateur')
        return Emprunt.objects.filter(utilisateur=user).select_related('livre')
    
    def perform_create(self, serializer):
        serializer.save(utilisateur=self.request.user)


class ProfilViewSet(viewsets.ModelViewSet):
    serializer_class = ProfilLecteurSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ProfilLecteur.objects.filter(utilisateur=self.request.user)
    
    def get_object(self):
        profil, created = ProfilLecteur.objects.get_or_create(utilisateur=self.request.user)
        return profil
    
    @action(detail=False, methods=['post'], url_path='favoris')
    def ajouter_favoris(self, request):
        livre_id = request.data.get('livre_id')
        if not livre_id:
            return Response({'erreur': 'livre_id requis'}, status=status.HTTP_400_BAD_REQUEST)
        
        livre = get_object_or_404(Livre, id=livre_id)
        profil = self.get_object()
        profil.livres_favoris.add(livre)
        return Response({'message': f'Livre "{livre.titre}" ajouté aux favoris'})


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]