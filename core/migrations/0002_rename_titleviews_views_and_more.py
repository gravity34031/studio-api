# Generated by Django 4.2.2 on 2023-06-27 13:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='TitleViews',
            new_name='Views',
        ),
        migrations.RenameIndex(
            model_name='views',
            new_name='core_views_content_145b34_idx',
            old_name='core_titlev_content_e48fec_idx',
        ),
    ]
