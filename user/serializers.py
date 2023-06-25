from datetime import date
from rest_framework import serializers
from .models import *
from core.models import TitleRating
from comments.models import Comment
from core.serializers import TitleListSerializer
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from django.core.validators import URLValidator

from django.contrib.auth import get_user_model
User = get_user_model()

from core.custom_moduls.image_management import deleteImage
from .custom_moduls.image_management import create_avatar



class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            'username', #30
            'password',
            'password2',
            'display_name',
            'avatar',
        )
        extra_kwargs = {
            'username': {'max_length': 30},
            'display_name': {'max_length': 30}
        }

    def validate(self, data):
        password = data.get('password')
        password2 = data.get('password2')
        if password != password2:
            raise serializers.ValidationError({'detail': 'Ошибка. Пароли не совпадают'})
        return data


    def create(self, validated_data):
        username = validated_data.get('username')
        display_name = validated_data.get('display_name', username)
        # if request doesn't contain avatar then generate it automaticly
        avatar = validated_data.get('avatar', create_avatar(display_name, username))

        user = User.objects.create(
            username = username,
            display_name = display_name,
            avatar = avatar
        )

        user.set_password(validated_data.get('password'))
        user.save()

        return user



class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'avatar',
            'display_name',
            'email',
            'first_name', #15
            'last_name', #25
            'sex',
            'birthday',
            'age',
            'contacts',
            'date_joined',
        )



class ChangeProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'avatar',
            'display_name',
            'email',
            'first_name', #15
            'last_name', #25
            'sex',
            'birthday',
            'age',
            'contacts'
        )
        extra_kwargs = {
            'first_name': {'max_length': 15},
            'last_name': {'max_length': 25},
            'age': {'read_only': True}
        }

    def validate_birthday(self, birthday):
        agedelta = (date.today() - birthday).days
        if agedelta < 0:
            raise serializers.ValidationError('Врата Штейна пересмотрел что ли?')
        elif agedelta == 0:
            raise serializers.ValidationError('С днем рождения!')
        return birthday

    def validate_contacts(self, contacts):
        if type(contacts) is not dict:
            raise serializers.ValidationError('Поле contacts должно быть формата JSON')
        
        # validate all fields in contacts that they are all correct url
        validate_url = URLValidator()
        for key, value in contacts.items():
            try:
                validate_url(value)
            # change validation message
            except exceptions.ValidationError as e:
                raise serializers.ValidationError(f'URL в поле {key} является некорректным')
        return contacts

    def update(self, instance, validated_data):
        sex = validated_data.get('sex')
        if sex == -1:
            validated_data['sex'] = None

        avatar = validated_data.get('avatar', False)
        if avatar or avatar is None: # if there is avatar in request and it's file or it's null
            instance_avatar = instance.avatar
            # delete old avatar
            deleteImage(instance_avatar)
            if avatar is None: # if avatar in request is null and exists
                # create auto-avatar
                display_name = validated_data.get('display_name', instance.display_name)
                username = instance.username
                avatar = create_avatar(display_name, username)
                validated_data['avatar'] = avatar
            
        instance = super().update(instance, validated_data)
        return instance



class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128, write_only=True, required=True)
    new_password = serializers.CharField(max_length=128, write_only=True, required=True)
    new_password2 = serializers.CharField(max_length=128, write_only=True, required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Введен неправильный текущий пароль')
        return value
        
    def validate(self, data):
        old_password = data['old_password']
        password = data['new_password']
        password2 = data['new_password2']
        if old_password == password:
            raise serializers.ValidationError('Новый пароль не может совпадать со старым')
        if password != password2:
            raise serializers.ValidationError('Пароли не совпадают')
        validate_password(password, self.context['request'].user)
        return data

    def save(self, **kwargs):
        password = self.validated_data['new_password']
        user = self.context['request'].user
        user.set_password(password)
        user.save()
        return user



class UserCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'avatar',
            'first_name',
            'last_name',
            'email'
        )



class RatedTitlesSerializer(TitleListSerializer):
    # add field your_rating to the TitleListSerializer
    def get_fields(self):
        fields = super().get_fields()
        fields['your_rating'] = serializers.SerializerMethodField()
        return fields



class ContentObjectRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        class_name = str(type(value).__name__)
        return {'obj': class_name, 'slug': value.slug}

class CommentSerializer(serializers.ModelSerializer):
    content_object = ContentObjectRelatedField(read_only=True)
    author = UserCommentSerializer(read_only=True)
    class Meta:
        model = Comment
        fields = (
            'author',
            'body',
            'create_time',
            'update_time',
            'content_object'
        )



