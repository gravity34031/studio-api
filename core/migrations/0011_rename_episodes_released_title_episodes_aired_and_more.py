# Generated by Django 4.2.2 on 2023-06-14 10:39

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_rename_episodes_realesed_title_episodes_released_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='title',
            old_name='episodes_released',
            new_name='episodes_aired',
        ),
        migrations.RemoveField(
            model_name='title',
            name='season',
        ),
        migrations.AddField(
            model_name='title',
            name='aired_on',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='Дата выхода аниме'),
            preserve_default=False,
        ),
    ]