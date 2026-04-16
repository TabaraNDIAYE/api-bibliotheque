# api/admin.py
from django.contrib import admin
from django.contrib.auth.models import User
from .models import Auteur, Livre, Tag, Emprunt, ProfilLecteur


@admin.register(Auteur)
class AuteurAdmin(admin.ModelAdmin):
    list_display = ['nom', 'nationalite', 'date_creation']
    search_fields = ['nom', 'nationalite']
    list_filter = ['nationalite']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['nom']
    search_fields = ['nom']


@admin.register(Livre)
class LivreAdmin(admin.ModelAdmin):
    list_display = ['titre', 'auteur', 'annee_publication', 'categorie', 'disponible']
    list_filter = ['categorie', 'disponible', 'auteur']
    search_fields = ['titre', 'isbn', 'auteur__nom']
    filter_horizontal = ['tags']


@admin.register(Emprunt)
class EmpruntAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'livre', 'date_emprunt', 'date_retour_prevue', 'rendu']
    list_filter = ['rendu', 'date_emprunt']
    search_fields = ['utilisateur__username', 'livre__titre']
    raw_id_fields = ['utilisateur', 'livre']


@admin.register(ProfilLecteur)
class ProfilLecteurAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'telephone', 'date_naissance']
    search_fields = ['utilisateur__username', 'telephone']
    filter_horizontal = ['livres_favoris']


# Signal pour créer automatiquement un profil lors de la création d'un utilisateur
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        ProfilLecteur.objects.create(utilisateur=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profil'):
        instance.profil.save()