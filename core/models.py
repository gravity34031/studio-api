import datetime
from functools import reduce
import os
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import UniqueConstraint
from django.utils.translation import gettext_lazy as _
from ckeditor_uploader.fields import RichTextUploadingField
from django_resized import ResizedImageField
from pytils import translit
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.fields import GenericRelation
from comments.models import Comment

from django.contrib.auth import get_user_model
User = get_user_model()

from .custom_moduls.models_func import get_img_path, get_img_thumb_path
from .custom_moduls.constants import DAYS_CHOICES


class Studio(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        img_path = 'studios/'
        self.img_path = img_path                                      # studios/
        self.img_thumbnail_path = os.path.join(img_path, 'thumbnail') # studios/thumbnail/

    title = models.CharField(_('Название'), max_length=50)
    slug = models.SlugField(unique=True, verbose_name="Слаг")
    description = models.TextField(verbose_name="Описание")
    photo = models.ImageField(_('Логотип'), max_length=128, upload_to=get_img_path)
    photo_thumbnail = ResizedImageField(_('Логотип мини'), size=[480, 150], crop=['middle', 'center'], force_format='WEBP', quality=90, max_length=128, upload_to=get_img_thumb_path)

    class Meta:
        ordering = ('title',)
        verbose_name = 'Студия'
        verbose_name_plural = 'Студии'

    def __str__(self):
        return self.title


class Actor(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        img_path = 'actors/'
        self.img_path = img_path                                      # actors/thumbnail/
        self.img_thumbnail_path = os.path.join(img_path, 'thumbnail') # actors/thumbnail/

    firstname = models.CharField(_('Имя'), max_length=70)
    secondname = models.CharField(_('Фамилия'), max_length=70)
    surname = models.CharField(_('Отчество'), max_length=70, blank=True, null=True) 
    slug = models.SlugField(unique=True, verbose_name='Слаг')
    photo = models.ImageField(_('Фото'), max_length=128, upload_to=get_img_path, blank=True, null=True)
    photo_thumbnail = ResizedImageField(_('Фото'), size=[320, 500], crop=['middle', 'center'], force_format='WEBP', quality=90, max_length=128, upload_to=get_img_thumb_path, blank=True, null=True)
    info = models.TextField(blank=True, null=True, verbose_name='Информация')

    class Meta:
        ordering = ('secondname', 'firstname', 'surname')
        verbose_name = 'Актер'
        verbose_name_plural = 'Актеры'

    def __str__(self):
        return f'{self.firstname} {self.secondname}'


class Genre(models.Model):
    title = models.CharField(_('Название'), max_length=50)
    slug = models.SlugField(unique=True, verbose_name='Слаг')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')

    class Meta:
        ordering = ('title',)
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.title



###
class Title(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        title_slug = self.slug

        paths = {'img_path': 'title/'}
        paths['poster_path'] = os.path.join(paths['img_path'], title_slug, 'poster')                     # title/<slug>/poster/
        paths['poster_thumbnail_path'] = os.path.join(paths['img_path'], title_slug, 'poster_thumbnail') # title/<slug>/poster_thumbnail/

        self.img_path = paths.get('img_path') # path to common folder
        self.poster_path = paths.get('poster_path')
        self.poster_thumbnail_path = paths.get('poster_thumbnail_path')

    title = models.CharField(max_length=120, verbose_name='Название')
    original_title = models.CharField(max_length=120, blank=True, null=True, default=None, verbose_name='Оригинальное название')
    # alternative_title = models.JSONField(blank=True, null=True, default=None, verbose_name='Альтернативные названия')
    slug = models.SlugField(unique=True, verbose_name='Слаг')
    description = models.TextField(_('Описание'))
    poster = models.ImageField(_('Постер'), max_length=128, upload_to=get_img_path)
    poster_thumbnail = ResizedImageField(_('Постер мини'), size=[378, 540], crop=['middle', 'center'], force_format='WEBP', quality=100, max_length=128, blank=True, upload_to=get_img_thumb_path)
    episodes = models.PositiveSmallIntegerField(_('Всего эпизодов'))
    episodes_aired = models.PositiveSmallIntegerField(_('Эпизодов вышло'))
    aired_on = models.DateField(_('Дата выхода аниме'))
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='titles', verbose_name='Автор поста')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    update_time = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')
    related_lists = models.ManyToManyField('self', blank=True, verbose_name='Связанные тайтлы')
    favourites = models.ManyToManyField(User, blank=True, related_name='favourite_titles', verbose_name='В избранном')

    studios = models.ManyToManyField(Studio, related_name='titles', verbose_name='Студия')
    actors = models.ManyToManyField(Actor, blank=True, related_name='titles', verbose_name='Актеры озвучивания')
    genres = models.ManyToManyField(Genre, related_name='titles', verbose_name='Жанр')

    comments = GenericRelation(Comment)

    class Meta:
        ordering = ('-create_time',)
        verbose_name = 'Тайтл'
        verbose_name_plural = 'Тайтлы'

    def __str__(self):
        return self.title

    @property
    def views(self):
        return TitleViews.objects.filter(title=self).count()

    # @property
    # def rating(self): # Average rating
    #     ratings = TitleRating.objects.filter(title=self).values('rating')
    #     if len(ratings) > 0:
    #         rating_sum = sum([i['rating'] for i in ratings])
    #         rating_avg = round(rating_sum / len(ratings), 1)
    #     else:
    #         rating_avg = None
    #     return rating_avg

    @property
    def status(self):
        status = ''
        if self.episodes_released >= self.episodes:
            status = 'Вышел'
        else:
            status = 'Онгоинг'
        return status
###


class AlternativeTitle(models.Model):
    anime = models.ForeignKey(Title, on_delete=models.CASCADE, related_name='alternative_title')
    title = models.CharField(max_length=120)


class AverageTitleRating(models.Model):
    title = models.OneToOneField(Title, related_name='average_rating', on_delete=models.CASCADE, primary_key=True, unique=True)
    rating = models.DecimalField(
        validators=
        [
            MinValueValidator(1),MaxValueValidator(10)
        ],
        max_digits=3, decimal_places=1,
        verbose_name='Средняя оценка'
    )
    voters = models.PositiveIntegerField(_('Количество проголосовавших'))

    def __str__(self):
        return f"title:<{str(self.title.title)}>; rating:<{self.rating}>"


class TitleViews(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE, related_name='title_views')
    ip = models.GenericIPAddressField(default="45.243.82.169", null=True)

    def __str__(self):
        return '{0} in {1} post'.format(self.ip,self.title)


class TitleRating(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE, related_name='title_rating', verbose_name='Тайтл')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='rating', verbose_name='Пользователь')
    rating = models.PositiveSmallIntegerField(
        validators=
        [
            MinValueValidator(1),MaxValueValidator(10)
        ], 
        verbose_name='Оценка'
    )

    class Meta:
        ordering = ('title', '-rating')
        unique_together = ('title', 'user')
        verbose_name = 'Рейтинг'
        verbose_name_plural = 'Рейтинг'

    def __str__(self):
        return f'{self.rating} - {self.title}, {self.user}'

    def save(self, *args, **kwargs): # Auto fill AverageTitleRating table. Need to rating in Title model
        super(TitleRating, self).save(*args, **kwargs)
        title_id = self.title_id
        if title_id:
            title = Title.objects.get(pk=title_id)
            if title:
                avg_rating, voters = self._get_rating_and_voters(title_id)
                AverageTitleRating.objects.update_or_create(title=title_id, defaults={'title': title, 'rating': avg_rating, 'voters': voters})
                # If AverageTitleRating with title_id exists then Update it with rating
                # Else create new one with {'title': title, 'rating': avg_rating}

    ### Funtions to create Average rating in Title model ###
    def _get_rating_and_voters(self, title_pk):
        ratings = TitleRating.objects.filter(title=title_pk).values('rating')
        avg_rating = self._get_avg_rating(ratings)
        voters = len(ratings)
        return avg_rating, voters

    def _get_avg_rating(self, ratings): # Average rating
        if len(ratings) > 0:
            rating_sum = sum([i['rating'] for i in ratings])
            rating_avg = round(rating_sum / len(ratings), 1)
        else:
            rating_avg = None
        return rating_avg
    ########################################################


class Frame(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        title_slug = self.title.slug
        title_img_path = self.title.img_path
        img_path = os.path.join(title_img_path, title_slug, 'frames')
        self.img_path = img_path                                       # title/<slug>/frames/
        self.img_thumbnail_path = os.path.join(img_path, 'thumbnails') # title/<slug>/frames/thumbnails/

    title = models.ForeignKey(Title, on_delete=models.CASCADE, related_name='frames', verbose_name='Тайтл')
    image = models.ImageField(_('Изображение'), max_length=128, upload_to=get_img_path)
    image_thumbnail = ResizedImageField(_('Изображение мини'), size=[480, 270], crop=['middle', 'center'], force_format='WEBP', quality=85, max_length=128, blank=True, upload_to=get_img_thumb_path)
    create_time = models.DateTimeField(_('Дата создания'), auto_now_add=True)

    class Meta:
        ordering = ('-create_time',)
        verbose_name = 'Кадр'
        verbose_name_plural = 'Кадры'

    def __str__(self):
        return str(self.title)


class Schedule(models.Model):
    title = models.OneToOneField(Title, on_delete=models.CASCADE, related_name='schedule', verbose_name='Тайтл')
    day = models.PositiveSmallIntegerField(choices=DAYS_CHOICES, null=False, verbose_name='День выхода')
    time = models.TimeField(null=True, blank=True, verbose_name='Время выхода')
    delay = models.DateTimeField(_('Дата при задержке'), null=True, blank=True, default=None)

    class Meta:
        ordering = ('day', 'time', 'title')
        verbose_name = 'Расписание'
        verbose_name_plural = 'Расписание'

    def _get_representation_day(self):
        return str(DAYS_CHOICES[self.day-1][1]) if self.day else 'unknown'

    @property
    def representation_day(self): # 1 ---> 'Понедельник'   2 ---> 'Вторник' etc.
        return self._get_representation_day()

    def __str__(self):
        return f"pk:<{str(self.pk)}> day:<{self._get_representation_day()}>"



#related_name    model.attribute_set