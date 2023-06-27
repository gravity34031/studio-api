# Generated by Django 4.2.2 on 2023-06-26 19:09

from django.db import migrations, models
import django_resized.forms


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0002_alter_youtubepost_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='youtubepost',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='youtubepost',
            name='image',
            field=django_resized.forms.ResizedImageField(blank=True, crop=['middle', 'center'], force_format='WEBP', keep_meta=True, max_length=128, quality=90, scale=None, size=[622, 350], upload_to='youtube_post', verbose_name='Фото'),
        ),
        migrations.AlterField(
            model_name='youtubepost',
            name='title',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]