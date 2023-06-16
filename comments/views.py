from django.shortcuts import get_object_or_404
from django.db.models import Count, F, Value, OuterRef, QuerySet, Prefetch
from .models import *
from .serializers import *
from rest_framework import viewsets, permissions, status, generics
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from django.contrib.contenttypes.models import ContentType

from rest_framework.filters import SearchFilter, OrderingFilter

from django.contrib.auth import get_user_model
User = get_user_model()


#from core.custom_moduls.paginators import TitleSetPagination

from core.models import Title
from content.models import News
str_to_model_dict = {'Title': Title, 'News': News} # Here you can add other models for comment



class GetCommentsView(GenericAPIView):
    serializer_class = CommentGetSerializer
    queryset = Comment.objects.all()

    def get_queryset(self):
        queryset = Comment.objects.none()
        request = self.request
        slug = self.kwargs.get('slug')
        content_type_param = request.query_params.get('content_type')
        if content_type_param:
            content_type = str_to_model_dict.get(str(content_type_param).title(), None)
            if content_type:
                post = get_object_or_404(content_type, slug=slug)
                queryset = post.comments.select_related('author').prefetch_related('content_object', Prefetch('comment_reaction', queryset=Reaction.objects.select_related('user')))

                
        return queryset


    def get(self, request, slug, *args, **kwargs):
        queryset = self.get_queryset()

        if queryset:      
            serializer = CommentGetSerializer(queryset, many=True, context={'request': request})
            return Response(serializer.data)
        return Response({'error': 'Данный контент не найден. Подсказка: укажите в параметрах запроса поле <content_type>, где задайте значение для конкретной модели. Пример: .../comments/magicheskaya-bitva/?content_type=title'})



class CommentView(GenericAPIView):
    serializer_class = CommentPostSerializer
    queryset = Comment.objects.all()

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        content_type_data = data.pop('content_type', None)
        if content_type_data:
            content_type = self.get_content_type(content_type_data)
            data['content_type'] = content_type
        
        serializer = self.serializer_class(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def get_content_type(self, raw_obj_str):
        obj_str = str(raw_obj_str[0]).title()
        model = str_to_model_dict.get(obj_str, None)
        if not model:
            return raw_obj_str
        return ContentType.objects.get_for_model(model).pk



class CommentRetrieveView(APIView):
    serializer_class = CommentPostSerializer
    queryset = Comment.objects.all()

    def get(self, request, pk, *args, **kwargs):
        instance = get_object_or_404(Comment, pk=pk)
        serializer = CommentGetSerializer(instance, context={'request': request})
        return Response(serializer.data)

    def patch(self, request, pk, *args, **kwargs):
        data = request.data
        instance = get_object_or_404(Comment, pk=pk)
        serializer = CommentPostSerializer(instance=instance, data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk, *args, **kwargs):
        instance = get_object_or_404(Comment, pk=pk)
        comment_has_replies = Comment.objects.filter(parent_id=pk).exists()
        if comment_has_replies:
            instance.author = None
            instance.body = None
            instance.is_deleted = True
            instance.save(update_fields=['author', 'body', 'is_deleted'])
            serializer = CommentGetSerializer(instance, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReactionCommentView(APIView):
    def get_queryset(self, *args, **kwargs):
        return Comment.objects.filter(reaction=self.request.user)

    def patch(self, request, pk, *args, **kwargs):
        data = request.data
        user = request.user
        reaction_status = data.get('status', None) # 0 is dislike; 1 is like; 'delete' for delete

        try:
            reaction_status = int(reaction_status)
        except ValueError:
            return Response({'error': 'status быть числом'}, status=status.HTTP_400_BAD_REQUEST)
        except TypeError:
            return Response({'error': 'В запросе отсутствует поле status. Добавьте status, где 1 - Лайк; 2 - Дизлайк'}, status=status.HTTP_400_BAD_REQUEST)

        if user:
            comment = get_object_or_404(Comment, pk=pk)
            reaction_obj = Reaction.objects.filter(user=user, comment=comment).first()

            if reaction_status == Reaction.DELETE: # if status in request = 0 (delete)
                if reaction_obj and user == comment.author: # if there is a reaction and user trying do delete his reaction
                    reaction_obj.delete()
                    return Response(status=status.HTTP_204_NO_CONTENT)
                else:
                    return Response({'error': 'Реакции уже не существует или это не твоя реакция'}, status=status.HTTP_400_BAD_REQUEST)

            reaction_status_choices = [i[0] for i in Reaction.REACTION_STATUS_CHOICES]
            if reaction_status in reaction_status_choices: # if status is correct

                if reaction_obj: # if there is a reaction
                    # if status was changed
                    if reaction_obj.status != reaction_status:
                        reaction_obj.status = reaction_status
                        reaction_obj.save(update_fields=['status'])
                else: # else create new
                    reaction_obj = Reaction.objects.create(comment=comment, user=user, status=reaction_status)

                serializer = ReactionSerializer(reaction_obj)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'В запросе отсутствует поле status или оно некорректно. Добавьте status, где 1 - Лайк; 2 - Дизлайк'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'data': 'Добавлять в избранное могут только авторизованные пользователи'}, status=status.HTTP_401_UNAUTHORIZED)





# make comment ordering (popularity/recent)



"""
This is the opposite of what the accepted answer is saying. Imagine the following:

class Comment(models.Model):
    body = models.TextField(verbose_name='Comment')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

class Post(models.Model):
    comment = GenericRelation(Comment)


In the above example, if your Comment object has a Generic Foreign Key pointing to a Post object, 
then when the Post object is deleted any Comment objects pointing to it will also be deleted.
"""