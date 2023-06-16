from rest_framework import serializers
from .models import *
from user.serializers import UserSerializer
from rest_framework_recursive.fields import RecursiveField

from django.contrib.auth import get_user_model
User = get_user_model()

from core.models import Title
from content.models import News

    ########author = UserSerializer(write_only=True)

class ContentObjectRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        class_name = str(type(value).__name__)
        return {'obj': class_name, 'slug': value.slug}


class FilterParentSerializer(serializers.ListSerializer):
    """Фильтр комментариев, только parents"""
    def to_representation(self, data):
        data = data.filter(parent=None)
        return super().to_representation(data)
    
class GetRecursiveSerializer(serializers.Serializer):
    """Вывод рекурсивно children"""
    def to_representation(self, value):
        # print(1)
        # print(value.pk)
        # print(self)
        # print(self.parent)
        #print(self.parent.parent)
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class CommentMixin(metaclass=serializers.SerializerMetaclass):
    # children = GetRecursiveSerializer(many=True, read_only=True)

    content_object = ContentObjectRelatedField(read_only=True)
    # reaction = serializers.SerializerMethodField(read_only=True)
    # your_reaction = serializers.SerializerMethodField(read_only=True)

    # def get_your_reaction(self, comment):
    #     if self.context:
    #         user = self.context.get('request').user
    #         if user:
    #             # if user left a reaction return his reaction
    #             # reaction_obj = Reaction.objects.filter(user=user, comment=comment).only('status').first()
    #             reaction_obj = comment.comment_reaction.filter(user=user).first()
    #             if reaction_obj:
    #                 return reaction_obj.status
    #     return None     

    def get_reaction(self, comment):
        reactions = {}

        if comment.comment_reaction.exists():
            print(comment.comment_reaction.all())
            
        for i in Reaction.REACTION_STATUS_CHOICES:
            count = comment.comment_reaction.filter(status=i[0]).count()
            react_name = i[1]
            reactions[react_name] = count
        return reactions


    class Meta:
        # list_serializer_class = FilterParentSerializer
        model = Comment
        fields = (
            # 'children',
            # 'your_reaction',
            'reactions',
            'pk',
            'author',
            'body',
            'create_time',
            'update_time',
            # 'reaction',
            'is_deleted',
            'content_object',
            'parent',
            'content_type',
            'object_id',
            
        )

        extra_kwargs = {
            'content_type': {'write_only': True},
            'object_id': {'write_only': True},
            'pk': {'read_only': True},
            'is_deleted': {'read_only': True}
        }

class CommentGetSerializer(CommentMixin, serializers.ModelSerializer):
    # author = UserSerializer()
    pass

        
class CommentPostSerializer(CommentMixin, serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate(self, data):
        # check if model with id exists
        content_type = data.get('content_type', None)
        object_id = data.get('object_id', None)
        if content_type and object_id:
            class_name = content_type.model_class()
            if not class_name.objects.filter(slug=object_id).exists():
                raise serializers.ValidationError({'error': f'Модель {class_name.__name__} не содежит объект со значением id={object_id}'})

        # check parent comment id != current comment
        instance = self.instance
        if instance:
            pk = instance.pk
            parent = data.get('parent', None)
            if parent:
                if parent.pk == pk:
                    raise serializers.ValidationError({'error': 'Комментарий не может быть родителем для самого себя'})

            if instance.is_deleted:
                raise serializers.ValidationError({'error': 'Комментарий удален. Изменить нельзя'})


        return data

    def get_fields(self): # make content_type and object_id can't be changed in patch
        fields = super().get_fields()
        request = self.context.get('request', None)
        if request and getattr(request, 'method', None) == "PATCH":
            for field in fields:
                if field in ('content_type', 'object_id', 'parent', 'author'):
                    fields[field].required = False
                    fields[field].read_only = True
        return fields



class ReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reaction
        fields = (
            'comment',
            'user',
            'status'
        )