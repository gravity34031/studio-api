from django.db import models
from django.utils.translation import gettext_lazy as _
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.contenttypes.fields import GenericRelation
from comments.models import Comment

from django.contrib.auth import get_user_model
User = get_user_model()
# Create your models here.


class News(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    body = RichTextUploadingField()
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0, verbose_name='Просмотры')

    class Meta:
        ordering = ('-create_time',)
        verbose_name = 'Новости'
        verbose_name_plural = 'Новости'
    
    def __str__(self):
        return self.title


class YoutubePost(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField()
    link = models.URLField()
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='youtube_posts')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0, verbose_name='Просмотры')

    comments = GenericRelation(Comment)

    class Meta:
        ordering = ('-create_time',)
        verbose_name = 'Ютуб видео'
        verbose_name_plural = 'Ютуб видео'
    
    def __str__(self):
        return self.title