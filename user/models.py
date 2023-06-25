from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django_resized import ResizedImageField
from django.utils.translation import gettext_lazy as _

from .custom_moduls.constants import AVATAR_SIZE # [150,150]


class User(AbstractUser):
    SEX_CHOICES = (
        (-1, None),
        (0, 'female'),
        (1, 'male')
    )
    display_name = models.CharField(_("Отображаемое имя"), max_length=40, blank=True)
    avatar = ResizedImageField(_("Аватар"), upload_to='avatar/', size=AVATAR_SIZE, force_format='WEBP', quality=100, crop=['middle', 'center'], max_length=128, blank=True, null=True)
    sex = models.SmallIntegerField(_("Пол"), choices=SEX_CHOICES, blank=True, null=True)
    birthday = models.DateField(_("Дата рождения"), blank=True, null=True)
    contacts = models.JSONField(blank=True, null=True, default=None)

    @property
    def age(self):
        current_date = date.today()
        birthday = self.birthday
        dym = relativedelta(current_date, birthday)
        years, months, days = dym.years, dym.months, dym.days
        return {'years': years, 'months': months, 'days': days}





# class Contacts(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contacts')
#     vk = models.URLField(blank=True, null=True, default=None)
#     telegram = models.URLField(blank=True, null=True, default=None)
