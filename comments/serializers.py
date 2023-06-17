from rest_framework import serializers
from .models import *
from user.serializers import CommentUserSerializer
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
    """Display only comment that has no parents (do not display childs)"""
    def to_representation(self, data):
        # data = data.filter(parent=None)
        if self.context.get('filtered_parent'):
            return super().to_representation(self.context.get('filtered_parent'))
        return super().to_representation(data)


class ChildrenSerializer(serializers.Serializer):
    """Display childs. Return serializer that refers to itself"""
    def to_representation(self, value):
        # CommentGetSerializer(...) is equal to:
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class CommentMixin(metaclass=serializers.SerializerMetaclass):
    content_object = ContentObjectRelatedField(read_only=True)
    children = ChildrenSerializer(many=True, read_only=True)

    reaction = serializers.SerializerMethodField(read_only=True)
    your_reaction = serializers.SerializerMethodField(read_only=True)

    def get_your_reaction(self, comment):
        # for num, name in Reaction.REACTION_STATUS_CHOICES:
        #     if num == comment.t2:
        #         return name
        if hasattr(comment, 'your_react'):
            return comment.your_react
        

    def get_reaction(self, comment):
        """
        Dynamic set value in dict 'reactions' to it value in comment.<attr> Like so:
        reactions['Dislike'] = comment.Dislike
        reactions['Like'] = comment.Like
        """
        reactions = {}
        for i in Reaction.REACTION_STATUS_CHOICES:
            if hasattr(comment, i[1]):
                reactions[i[1]] = getattr(comment, i[1])
        return reactions 
        # for i in Reaction.REACTION_STATUS_CHOICES:
        #     count = comment.comment_reaction.filter(status=i[0]).count()
        #     react_name = i[1]
        #     reactions[react_name] = count
        # return reactions


    class Meta:
        list_serializer_class = FilterParentSerializer
        model = Comment
        fields = (
            'pk',
            'author',
            'body',
            'create_time',
            'update_time',
            'your_reaction',
            'reaction',
            'rating',
            'is_deleted',
            'content_object',
            'parent',
            'children',
            'content_type', # w_o
            'object_id',    # w_o
            
        )

        extra_kwargs = {
            'content_type': {'write_only': True},
            'object_id': {'write_only': True},
            'pk': {'read_only': True},
            'is_deleted': {'read_only': True},
            'rating': {'read_only': True}
        }

class CommentGetSerializer(CommentMixin, serializers.ModelSerializer):
    author = CommentUserSerializer(read_only=True)
        
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