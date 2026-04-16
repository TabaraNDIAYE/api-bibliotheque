# api/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Auteur, Livre, Tag, Emprunt, ProfilLecteur


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'nom']


class AuteurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auteur
        fields = '__all__'
        read_only_fields = ['id', 'date_creation']


class AuteurDetailSerializer(serializers.ModelSerializer):
    livres = serializers.SerializerMethodField()

    class Meta:
        model = Auteur
        fields = ['id', 'nom', 'biographie', 'nationalite', 'date_creation', 'livres']

    def get_livres(self, obj):
        return [{'id': l.id, 'titre': l.titre, 'annee_publication': l.annee_publication} 
                for l in obj.livres.all()]


class LivreSerializer(serializers.ModelSerializer):
    auteur_nom = serializers.SerializerMethodField(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        source='tags',
        write_only=True,
        required=False
    )

    class Meta:
        model = Livre
        fields = [
            'id', 'titre', 'isbn', 'annee_publication', 'categorie',
            'auteur', 'auteur_nom', 'tags', 'tag_ids', 'disponible', 
            'cree_par', 'date_creation'
        ]
        read_only_fields = ['id', 'cree_par', 'date_creation']

    def get_auteur_nom(self, obj):
        return obj.auteur.nom if obj.auteur else None

    def validate_isbn(self, value):
        clean = value.replace('-', '')
        if not clean.isdigit() or len(clean) != 13:
            raise serializers.ValidationError("L'ISBN doit contenir exactement 13 chiffres.")
        return value

    def validate_annee_publication(self, value):
        if value < 1000 or value > 2025:
            raise serializers.ValidationError("L'année doit être entre 1000 et 2025.")
        return value

    def validate(self, data):
        if data.get('categorie') == 'essai':
            auteur = data.get('auteur')
            if auteur and not auteur.biographie:
                raise serializers.ValidationError(
                    "Les essais requièrent une biographie de l'auteur."
                )
        return data


class LivreDetailSerializer(LivreSerializer):
    auteur = AuteurSerializer(read_only=True)

    class Meta(LivreSerializer.Meta):
        fields = LivreSerializer.Meta.fields + ['auteur']
        read_only_fields = LivreSerializer.Meta.read_only_fields


class EmpruntSerializer(serializers.ModelSerializer):
    livre_titre = serializers.CharField(source='livre.titre', read_only=True)
    utilisateur_nom = serializers.CharField(source='utilisateur.username', read_only=True)

    class Meta:
        model = Emprunt
        fields = ['id', 'utilisateur', 'utilisateur_nom', 'livre', 'livre_titre', 
                  'date_emprunt', 'date_retour_prevue', 'rendu']
        read_only_fields = ['id', 'date_emprunt']


class ProfilLecteurSerializer(serializers.ModelSerializer):
    utilisateur_nom = serializers.CharField(source='utilisateur.username', read_only=True)
    livres_favoris_details = LivreSerializer(source='livres_favoris', many=True, read_only=True)
    livres_favoris_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Livre.objects.all(),
        source='livres_favoris',
        write_only=True,
        required=False
    )

    class Meta:
        model = ProfilLecteur
        fields = ['id', 'utilisateur', 'utilisateur_nom', 'adresse', 'telephone', 
                  'date_naissance', 'livres_favoris', 'livres_favoris_details', 'livres_favoris_ids']
        read_only_fields = ['id', 'utilisateur']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']