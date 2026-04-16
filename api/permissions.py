# api/permissions.py
from rest_framework import permissions

class EstProprietaireOuReadOnly(permissions.BasePermission):
    """
    Permission personnalisée:
    - Lecture: tout le monde
    - Écriture/modification/suppression: uniquement le propriétaire ou admin
    """
    
    def has_permission(self, request, view):
        # Lecture autorisée à tous
        if request.method in permissions.SAFE_METHODS:
            return True
        # Écriture nécessite authentification
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Lecture toujours autorisée
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Vérifier si l'objet a un attribut 'cree_par'
        if hasattr(obj, 'cree_par'):
            return obj.cree_par == request.user or request.user.is_staff
        
        return request.user.is_staff


class EstProprietaireEmprunt(permissions.BasePermission):
    """Un utilisateur ne peut voir/modifier que ses propres emprunts"""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        return obj.utilisateur == request.user or request.user.is_staff