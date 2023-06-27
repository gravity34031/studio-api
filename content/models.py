from django.db import models
from django.utils.translation import gettext_lazy as _
from ckeditor_uploader.fields import RichTextUploadingField
from django_resized import ResizedImageField
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from comments.models import Comment
from core.models import Views

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

    comments = GenericRelation(Comment)
    news_views = GenericRelation(Views)

    @property
    def views(self):
        # content_type = ContentType.objects.get_for_model(self)
        # return Views.objects.filter(content_type=content_type, object_id=self.pk).count()
        return self.views_count
    class Meta:
        ordering = ('-create_time',)
        verbose_name = 'Новости'
        verbose_name_plural = 'Новости'
    
    def __str__(self):
        return self.title


class YoutubePost(models.Model):
    title = models.CharField(max_length=100, blank=True)
    description = models.TextField(null=True, blank=True)
    image = ResizedImageField(_('Фото'), size=[622, 350], crop=['middle', 'center'], force_format='WEBP', quality=90, max_length=128, upload_to='youtube_post', blank=True)
    link = models.URLField()
    # link UNIQUE = TRUE
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='youtube_posts')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-create_time',)
        verbose_name = 'Ютуб видео'
        verbose_name_plural = 'Ютуб видео'
    
    def __str__(self):
        return self.title