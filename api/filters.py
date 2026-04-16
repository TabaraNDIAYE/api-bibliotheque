# api/filters.py
import django_filters
from .models import Livre

class LivreFilter(django_filters.FilterSet):
    categorie = django_filters.ChoiceFilter(choices=Livre.CATEGORIES)
    disponible = django_filters.BooleanFilter()
    annee_min = django_filters.NumberFilter(field_name='annee_publication', lookup_expr='gte')
    annee_max = django_filters.NumberFilter(field_name='annee_publication', lookup_expr='lte')
    titre_contient = django_filters.CharFilter(field_name='titre', lookup_expr='icontains')
    auteur_nom = django_filters.CharFilter(field_name='auteur__nom', lookup_expr='icontains')

    class Meta:
        model = Livre
        fields = ['categorie', 'disponible', 'annee_min', 'annee_max']