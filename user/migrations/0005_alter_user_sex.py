# Generated by Django 4.2.2 on 2023-06-25 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_remove_user_age_user_birthday_alter_user_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='sex',
            field=models.BooleanField(blank=True, choices=[(-1, None), (0, 'female'), (1, 'male')], null=True, verbose_name='Пол'),
        ),
    ]
