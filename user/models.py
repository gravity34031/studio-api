from django.contrib.auth.models import AbstractUser
from django.db import models
from django_resized import ResizedImageField
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    avatar = ResizedImageField(_("profile avatar"), size=[150, 150], force_format='WEBP', quality=100, crop=['middle', 'center'], max_length=128, blank=True, null=True)
    IS_MAN_CHOICES = (
        (True, 'male'),
        (False, 'female')
    )
    sex = models.BooleanField(choices=IS_MAN_CHOICES, blank=True, null=True)
    age = models.DateField(blank=True, null=True)
    contacts = models.JSONField(blank=True, null=True)