# Generated by Django 4.2.2 on 2023-06-27 13:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0004_remove_youtubepost_views'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='news',
            name='views',
        ),
    ]
