from django.db import models
from django.utils.translation import gettext_lazy as _
# from core.models import Title
# from content.models import News
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django.contrib.auth import get_user_model
User = get_user_model()
# Create your models here.


class Comment(models.Model):
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, default=None, related_name='children') # parent comment for replied comment
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=False, related_name='comments')
    body = models.TextField(null=True, blank=False)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    reaction = models.ManyToManyField(User, blank=True, related_name='reaction_comments', through='Reaction')
    rating = models.PositiveBigIntegerField(default=0)
    is_deleted = models.BooleanField(blank=True, default=False)

    content_type = models.ForeignKey(ContentType, on_delete=models.RESTRICT)
    object_id = models.PositiveBigIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

        ordering = ('-create_time',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
    
    def __str__(self):
        parent = None
        if self.parent is not None:
            parent = self.parent.pk
        return f'{parent} - {self.author} {self.body}'

    def save(self, *args, **kwargs):
        initial_parent = self._get_initial_parent(self.parent)
        self.parent = initial_parent

        super().save(*args, **kwargs)

    def _get_initial_parent(self, comment):
        if comment is not None: # if there is parent in request
            if comment.parent is None:
                return comment
            else: # if comment is children and it has parent <find parent of the parent of the comment>
                return self.get_initial_parent(comment.parent)
        else:
            return None

    def _get_rating(self):
        reaction = self.comment_reaction
        dislikes = reaction.filter(status=0).count()
        likes = reaction.filter(status=1).count()
        return likes - dislikes


class Reaction(models.Model):
    DELETE = -1
    DISLIKE = 0
    LIKE = 1
    REACTION_STATUS_CHOICES = [
        (DISLIKE, 'Dislike'),
        (LIKE, 'Like'),
    ]
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='comment_reaction')
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    status = models.PositiveSmallIntegerField(choices=REACTION_STATUS_CHOICES)

    def __str__(self):
        return f'{self.user}, {self.status}, {self.comment}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Update comment's rating
        comment= self.comment
        comment.rating = comment._get_rating()
        comment.save(update_fields=['rating'])


        





# title = Title(...)
# title.save()
# News = News(...)
# News.save()

# t_comment = Comment(content_object=title, author=..., ...)
# t_comment.save()

# n_comment = Comment(content_object=news, author=..., ...)
# n_comment.save()

# t_comment.content_object  # Is the instance of the title
# n_comment.content_object  # Is the instance of the news