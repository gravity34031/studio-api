from rest_framework import serializers
from .models import *

from django.contrib.auth import get_user_model
User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields='__all__'



class CommentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'avatar',
            'first_name',
            'last_name',
            'email'
        )