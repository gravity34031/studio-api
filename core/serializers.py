from rest_framework import serializers
from core.models import *
from django.conf import settings
from textdistance import overlap as text_similarity

from django.contrib.auth import get_user_model
User = get_user_model()

from .custom_moduls.image_management import deleteImage
from .custom_moduls.constants import PERCENT_OF_SIMILARITY_FOR_RELATED_TITLES
from .custom_moduls.serialize_func import create_alternative_title, create_related_titles




class AutoDelImgMixin(metaclass=serializers.SerializerMetaclass):
    def create(self, validated_data):
        # make photo_thumbnail == photo
        validated_data['photo_thumbnail'] = validated_data.get('photo')
        instance = super().create(validated_data)
        return instance
    
    def update(self, instance, validated_data):
        # make photo_thumbnail == photo
        validated_data['photo_thumbnail'] = validated_data.get('photo')
        image = instance.photo
        image_thumbnail = instance.photo_thumbnail
        instance = super().update(instance, validated_data)
        
        # del old photo and thumbnail if it had been changed
        if image:
            for img in (image, image_thumbnail):
                deleteImage(img)
        return instance

class StudioSerializer(AutoDelImgMixin, serializers.ModelSerializer):
    class Meta:
        model = Studio
        fields = ('title', 'slug', 'description', 'photo')
        extra_kwargs = {
            'url': {'lookup_field': 'slug'},
        }

class ActorSerializer(AutoDelImgMixin, serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ('firstname', 'secondname', 'surname', 'slug', 'photo', 'info')
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }



class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('title', 'slug', 'description')
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }



class ScheduleMixin(metaclass=serializers.SerializerMetaclass):
    class Meta:
        model = Schedule
        fields = ('pk', 'day', 'time', 'delay', 'title')



class FrameSerializer(serializers.ModelSerializer):
    title = serializers.SlugRelatedField(slug_field='slug', queryset=Title.objects.all())
    class Meta:
        model = Frame
        fields = ('pk', 'title', 'image', 'image_thumbnail')

    def create(self, validated_data):
        # make image_thumbnail == image
        validated_data['image_thumbnail'] = validated_data.get('image')
        instance = super().create(validated_data)
        return instance



class AlternativeTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlternativeTitle
        fields = ('title', )

class TitleRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = AverageTitleRating
        fields = ('rating', 'voters')



class TitleMixin(metaclass=serializers.SerializerMetaclass):
    author = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all(), default=serializers.CurrentUserDefault())
    frames = FrameSerializer(many=True, required=False, write_only=True)
    average_rating = TitleRatingSerializer(read_only=True)
    alternative_title = AlternativeTitleSerializer(read_only=True, many=True)

    studios = StudioSerializer(many=True)
    actors = ActorSerializer(many=True)
    genres = GenreSerializer(many=True)
    favourites = serializers.SerializerMethodField()
    schedule = serializers.SerializerMethodField()
    your_rating = serializers.SerializerMethodField()
    your_favourite = serializers.SerializerMethodField()

    def get_your_rating(self, title):
        if self.context:
            user = self.context.get('request').user
            if user:
                # if user rated title return his rating
                rating_obj = TitleRating.objects.filter(title=title, user=user).first()
                if rating_obj:
                    return rating_obj.rating
        return None

    def get_your_favourite(self, title):
        if self.context:
            user = self.context.get('request').user
            if user:
                # if user added title to favourite
                rating_obj_exists = user.favourite_titles.filter(slug=title.slug).exists()
                if rating_obj_exists:
                    return rating_obj_exists
        return False

    def get_favourites(self, title):
        return title.favourites.count()

    def get_schedule(self, title):
        if hasattr(title, 'schedule'):
            schedule = title.schedule
            return {'day': schedule.representation_day, 'time': schedule.time, 'delay': schedule.delay}
        return None

    class Meta:
        model = Title
        fields = (
            'pk',
            'title',
            'original_title',
            'slug',
            'poster',
            'poster_thumbnail',
            'description',
            'alternative_title',
            'aired_on',
            'episodes',
            'episodes_aired',
            'status',
            'create_time',
            'update_time',
            'your_rating',
            'average_rating',
            'your_favourite',
            'favourites',
            'views',
            'schedule',
            'genres',
            'studios',
            'actors',
            'related_lists',
            'frames',
            'author'
        )
        extra_kwargs = {
            'schedule': {'read_only': True, 'allow_null': True}
        }

class TitleListSerializer(TitleMixin, serializers.ModelSerializer):
    class Meta:
        model = Title
        fields = (
            'pk',
            'title',
            'original_title',
            'slug',
            'poster_thumbnail',
            'description',
            'average_rating',
            'aired_on',
            'episodes',
            'episodes_aired',
            'status',
            'genres',
        )

class TitleGetSerializer(TitleMixin, serializers.ModelSerializer):
    related_lists = TitleListSerializer(read_only=True, many=True)

class TitlePostSerializer(TitleMixin, serializers.ModelSerializer):
    studios = serializers.SlugRelatedField(slug_field='slug', queryset=Studio.objects.all(), many=True)
    actors = serializers.SlugRelatedField(slug_field='slug', queryset=Actor.objects.all(), many=True)
    genres = serializers.SlugRelatedField(slug_field='slug', queryset=Genre.objects.all(), many=True)
    alternative_title = serializers.CharField(max_length=300, required=False, write_only=True, allow_null=True)
    related_lists = serializers.CharField(max_length=1000, required=False, write_only=True, allow_null=True)
    
    
    def validate(self, data): # validate ep_realeased always lower than total episodes
        instance = self.instance
        ep = data.get('episodes', None)
        if not ep:
            ep = instance.episodes
        ep_aired = data.get('episodes_aired', None)
        if not ep_aired:
            ep_aired = instance.episodes_aired
        if ep_aired:
            if ep_aired < 0:
                raise serializers.ValidationError({'error': 'Количество вышедших эпизодов не может быть меньше 0'})
            if ep_aired > ep:
                raise serializers.ValidationError({'error': 'Количество вышедших эпизодов не может быть больше чем всего эпизодов'})
        return data

    
    def create(self, validated_data):
        alternative_title_data = validated_data.pop('alternative_title', None)
        related_lists_data = str(validated_data.pop('related_lists', None))

        # make poster_thumbnail == poster
        validated_data['poster_thumbnail'] = validated_data.get('poster')
        instance = super().create(validated_data)

        # auto create AlternativeTitle model and relate it to the title
        if alternative_title_data:
            create_alternative_title(instance=instance, alternative_title_data=alternative_title_data)

        # create related_lists
        auto_related = self.context.get('auto_related')
        create_related_titles(instance=instance, auto_related=auto_related, related_lists_data=related_lists_data)
                
        return instance


    def update(self, instance, validated_data):
        alternative_title_data = validated_data.pop('alternative_title', False)
        related_lists_data = str(validated_data.pop('related_lists', None))

        # make poster_thumbnail == poster
        validated_data['poster_thumbnail'] = validated_data.get('poster')
        instance = super().update(instance, validated_data)

        # auto create AlternativeTitle model and relate it to the title
        if alternative_title_data is not False: # if alternative_title was in request 
            old_alt_titles_instance = AlternativeTitle.objects.filter(anime=instance)
            old_alt_titles_instance.delete() # del old alternative_title
            if alternative_title_data is not None: # if there is new alt_titles in request then create
                create_alternative_title(instance=instance, alternative_title_data=alternative_title_data)

        # create related_lists
        auto_related = self.context.get('auto_related')
        create_related_titles(instance=instance, auto_related=auto_related, related_lists_data=related_lists_data, update=True)
         
        return instance



class ScheduleGetSerializer(ScheduleMixin, serializers.ModelSerializer):
    title = TitleListSerializer()

class SchedulePostSerializer(ScheduleMixin, serializers.ModelSerializer):
    title = serializers.SlugRelatedField(slug_field='slug', queryset=Title.objects.all())

    def validate(self, data): # exlude UNIQUE field (title) error
        if data.get('title', None):
            if Schedule.objects.filter(title=data['title']).exists():   
                raise serializers.ValidationError(
                    {'error': 'Поле title должно быть уникальным'})
        return data



class RatingSerializer(serializers.ModelSerializer):
    title = serializers.SlugRelatedField(slug_field='slug', queryset=Title.objects.all())
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = TitleRating
        fields = ('pk', 'title', 'user', 'rating')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=TitleRating.objects.all(),
                fields=('title', 'user'),
                message="Пользователь уже поставил рейтинг на этот тайтл"
            )
        ]












# def get_frames(self, title):
#     request = self.context.get('request', None)
#     imgs = []
#     if request:
#         for frame in Frame.objects.filter(title=title):
#             imgs.append(request.build_absolute_uri(settings.MEDIA_URL+str(frame.image)))
#     return imgs

# def get_fields(self):
#     fields = super().get_fields()
#     request = self.context.get('request', None)
#     if request and getattr(request, 'method', None) == "POST":
#         if fields.get('frames', None):
#             fields['frames'] = serializers.SerializerMethodField()
#     return fields

# def put_fields_not_required(self, fields): # make all fields in put request is not required. 
#     request = self.context.get('request', None)
#     if request and getattr(request, 'method', None) == "PUT":
#         for field in fields:
#             fields[field].required = False
#     return fields

# def update(self, instance, validated_data): # need to avoid None img when sending 'put' without img
#     if instance.photo and not validated_data.get('photo', None):
#         validated_data['photo'] = instance.photo
#     return super().update(instance, validated_data)