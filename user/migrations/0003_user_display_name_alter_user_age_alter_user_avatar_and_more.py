# Generated by Django 4.2.2 on 2023-06-18 17:33

from django.db import migrations, models
import django_resized.forms


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_remove_user_contacts_contacts'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='display_name',
            field=models.CharField(blank=True, max_length=40, verbose_name='Отображаемое имя'),
        ),
        migrations.AlterField(
            model_name='user',
            name='age',
            field=models.DateField(blank=True, null=True, verbose_name='Возраст'),
        ),
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=django_resized.forms.ResizedImageField(blank=True, crop=['middle', 'center'], force_format='WEBP', keep_meta=True, max_length=128, null=True, quality=100, scale=None, size=[150, 150], upload_to='', verbose_name='Аватар'),
        ),
        migrations.AlterField(
            model_name='user',
            name='sex',
            field=models.BooleanField(blank=True, choices=[(True, 'male'), (False, 'female')], null=True, verbose_name='Пол'),
        ),
    ]