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
        return self.body

    @property
    def reactions(self):
        reactions_dict = {tup[0]: 0 for tup in Reaction.REACTION_STATUS_CHOICES}
        # print('----')






        for r in self.comment_reaction.all():
            reactions_dict[r.status] += 1


        # for i in Reaction.REACTION_STATUS_CHOICES:
        #     count = self.comment_reaction.filter(status=i[0]).count()
        #     react_name = i[1]
        #     reactions_dict[react_name] = count
        return reactions_dict



class Reaction(models.Model):
    DELETE = 0
    DISLIKE = 1
    LIKE = 2
    REACTION_STATUS_CHOICES = [
        (DISLIKE, 'Dislike'),
        (LIKE, 'Like'),
    ]
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='comment_reaction')
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    status = models.PositiveSmallIntegerField(choices=REACTION_STATUS_CHOICES)

    def __str__(self):
        return f'{self.user}, {self.status}, {self.comment}'



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