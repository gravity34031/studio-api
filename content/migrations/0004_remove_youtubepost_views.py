# Generated by Django 4.2.2 on 2023-06-26 19:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0003_alter_youtubepost_description_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='youtubepost',
            name='views',
        ),
    ]
