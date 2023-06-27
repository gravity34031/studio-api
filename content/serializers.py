import os
from rest_framework import serializers
from .models import *
from django.conf import settings

from django.contrib.auth import get_user_model
User = get_user_model()

from .custom_moduls.parser import get_oembed_data
from core.custom_moduls.image_management import deleteImage


class NewsSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all(), default=serializers.CurrentUserDefault())
    class Meta:
        model = News
        fields = (
            'pk',
            'title',
            'slug',
            'body',
            'create_time',
            'update_time',
            'author',
            'views',
        )

    

class YoutubeSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all(), default=serializers.CurrentUserDefault())
    class Meta:
        model = YoutubePost
        fields = (
            'pk',
            'link',
            'title',
            'description',
            'image',
            'create_time',
            'update_time',
            'author',
        )
        extra_kwargs={
            'title': {'allow_null': True},
            'image': {'allow_null': True}
        }

    err_url_not_found = {'error': 'Ошибка в url. Такого видео не существует'}

    def create(self, validated_data):
        link = validated_data.get('link')
        # get title and image using link automaticly
        parsed_data = get_oembed_data(link)

        title, image = None, None
        if 'title' not in validated_data:
            title = parsed_data.get('title')
            validated_data['title'] = title
        if 'image' not in validated_data:
            image = parsed_data.get('image')
            validated_data['image'] = image

        if not title and not image:
            raise serializers.ValidationError(self.err_url_not_found)


        instance = super().create(validated_data)
        return instance

    def update(self, instance, validated_data):
        title = validated_data.get('title', False)
        image = validated_data.get('image', False)
        auto_title, auto_image = None, None

        # title or image in request and at least one of them is empty
        if title in (None, '') or image in (None, ''):
            link = validated_data.get('link', instance.link)
            parsed_data = get_oembed_data(link)

            # if title in request and it's empty
            if title in (None, ''):
                auto_title = parsed_data.get('title')
                validated_data['title'] = auto_title

            # if image in request and it's empty
            if image in (None, ''):
                auto_image = parsed_data.get('image')
                validated_data['image'] = auto_image

            if not auto_title and not auto_image:
                raise serializers.ValidationError(self.err_url_not_found)

        # delete image if it had been changed
        instance_image = instance.image
        if instance_image:
            # del image
            image = validated_data.get('image')
            if image:
                image_path = os.path.join(str(instance_image))
                deleteImage(image_path)

        instance = super().update(instance, validated_data)
        return instance