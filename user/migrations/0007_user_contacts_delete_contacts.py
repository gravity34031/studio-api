# Generated by Django 4.2.2 on 2023-06-25 14:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0006_alter_user_sex'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='contacts',
            field=models.JSONField(blank=True, default=None, null=True),
        ),
        migrations.DeleteModel(
            name='Contacts',
        ),
    ]
