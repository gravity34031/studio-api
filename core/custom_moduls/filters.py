from django_filters import rest_framework as filters
from ..models import Title, Genre, Actor, Studio
from django.db.models import F, Case, When, Value





class TitleFilter(filters.FilterSet):
    rating = filters.NumberFilter(field_name='average_rating__rating', lookup_expr='gte')
    aired_on_from = filters.DateFilter(field_name='aired_on', lookup_expr='gte')
    aired_on_to = filters.DateFilter(field_name='aired_on', lookup_expr='lte')
    genres = filters.ModelMultipleChoiceFilter(field_name='genres', to_field_name='slug', queryset=Genre.objects.all())
    actors = filters.ModelMultipleChoiceFilter(field_name='actors', to_field_name='slug', queryset=Actor.objects.all())
    studios = filters.ModelMultipleChoiceFilter(field_name='studios', to_field_name='slug', queryset=Studio.objects.all())

    status = filters.CharFilter(field_name='status', method='get_status')

    class Meta:
        model = Title
        fields = (
            'average_rating__rating',
            'aired_on',
            'genres',
            'actors',
            'studios'
        )

    def get_status(self, queryset, name, value):
        queryset_with_status = queryset.annotate(name=Case(
            When(episodes_aired__gte=F('episodes'), then=Value("Вышел")),
            When(episodes_aired__lt=F('episodes'), then=Value('Онгоинг')),
            default=Value('Неизвестно')
        )) # add to queryset field status
        value = str(value).title() # make case - insensitive
        return queryset_with_status.filter(name=value) # filter by status