from django.shortcuts import get_object_or_404
from django.db.models import Count, Sum, F, Q, Value, Exists, OuterRef, QuerySet, Prefetch, FilteredRelation, Case, When
from .models import *
from .serializers import *
from rest_framework import viewsets, permissions, status, generics
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from django.contrib.contenttypes.models import ContentType

from rest_framework.filters import SearchFilter, OrderingFilter
from core.custom_moduls.paginators import CommentSetPagination

from django.contrib.auth import get_user_model
User = get_user_model()


#from core.custom_moduls.paginators import TitleSetPagination

from core.models import Title
from content.models import News
str_to_model_dict = {'Title': Title, 'News': News} # Here you can add other models for comment



class GetCommentsView(GenericAPIView):
    serializer_class = CommentGetSerializer
    queryset = Comment.objects.all()
    pagination_class = CommentSetPagination
    filter_backends = [OrderingFilter, SearchFilter]
    search_fields = ['body']
    ordering_fields = ('create_time', 'rating')
    ordering = ['-create_time']
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Comment.objects.none()
        request = self.request
        slug = self.kwargs.get('slug')
        content_type_param = request.query_params.get('content_type')
        if content_type_param:
            content_type = str_to_model_dict.get(str(content_type_param).title(), None)
            if content_type:
                post = get_object_or_404(content_type, slug=slug)
                queryset = post.comments.select_related('author').prefetch_related('content_object', Prefetch('comment_reaction', queryset=Reaction.objects.select_related('user'))) \

                """
                Adding child_queryset need to add annotation not only to comment but for it child too
                """
                child_queryset = Comment.objects.filter(~Q(parent=None)).prefetch_related('children', 'content_object').select_related('author').order_by('create_time')


                if request.user and request.user.is_authenticated:
                    queryset = queryset.annotate(your_react = Sum(Case(
                        When(comment_reaction__user=request.user, then=F('comment_reaction__status'))
                    )))
                    child_queryset = child_queryset.annotate(your_react = Sum(Case(
                        When(comment_reaction__user=request.user, then=F('comment_reaction__status'))
                    )))

                """ 
                Auto annotate queryset. Adding count of each reaction to the comment. Name of annotation is taken from Reaction.REACTION_STATUS_CHOICES
                Like this but dynamic and for all reactions:
                .annotate(Dislike=Count('comment_reaction', filter=Q(comment_reaction__status=1)))
                .annotate(Like=Count('comment_reaction', filter=Q(comment_reaction__status=2)))
                """
                for i in Reaction.REACTION_STATUS_CHOICES:
                    queryset = queryset.annotate(**{i[1]: Count('comment_reaction', filter=Q(comment_reaction__status=i[0]))})
                    child_queryset = child_queryset.annotate(**{i[1]: Count('comment_reaction', filter=Q(comment_reaction__status=i[0]))})

                # Prefetch queryset of childs to apply all changes in annotation
                queryset = queryset.prefetch_related(Prefetch('children', queryset=child_queryset  ))\

                
        return queryset



    def get(self, request, slug, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        if queryset:
            data_for_filter_parent_serializer = queryset.filter(parent=None) # need to add to context. exlude childs instance from data. childs only in parents comments
            context = {'request': request, 'filtered_parent': data_for_filter_parent_serializer}

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.serializer_class(page, many=True, context=context)
                return self.get_paginated_response(serializer.data)

            serializer = self.serializer_class(queryset, many=True, context=context)

            # serializer = CommentGetSerializer(queryset, many=True, context=context)
            return Response(serializer.data)
        return Response({'error': 'Данный контент не найден. Подсказка: укажите в параметрах запроса поле <content_type>, где задайте значение для конкретной модели. Пример: .../comments/magicheskaya-bitva/?content_type=title'})



class CommentView(GenericAPIView):
    serializer_class = CommentPostSerializer
    queryset = Comment.objects.all()
    permission_classes = [permissions.IsAuthenticated]

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
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Comment.objects.select_related('author').prefetch_related(
            Prefetch('children', queryset=Comment.objects.select_related('author').prefetch_related('children', 'content_object').order_by('create_time'))
            )
    

    def get(self, request, pk, *args, **kwargs):
        instance = get_object_or_404(self.get_queryset(), pk=pk)
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
        instance = get_object_or_404(self.get_queryset(), pk=pk)
        if instance.is_deleted == False and request.user == instance.author:
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
        return Response(status=status.HTTP_403_FORBIDDEN)


class ReactionCommentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        return Comment.objects.filter(reaction=self.request.user)

    def get_str_reaction_choices(self):
        reactions_constant = Reaction.REACTION_STATUS_CHOICES
        pretty_constant = "; ".join([f"{str(i[0])} - {str(i[1])}" for i in reactions_constant])
        return pretty_constant

    def patch(self, request, pk, *args, **kwargs):
        data = request.data
        user = request.user
        reaction_status = data.get('status', None) # 0 is dislike; 1 is like; 'delete' for delete

        try:
            reaction_status = int(reaction_status)
        except ValueError:
            return Response({'error': 'status быть числом'}, status=status.HTTP_400_BAD_REQUEST)
        except TypeError:
            return Response({'error': f'В запросе отсутствует поле status. Добавьте status, где {self.get_str_reaction_choices()}'}, status=status.HTTP_400_BAD_REQUEST)

        if user and user.is_authenticated:
            comment = get_object_or_404(Comment, pk=pk)
            reaction_obj = Reaction.objects.filter(user=user, comment=comment).first()

            # Deleting section
            if reaction_status == Reaction.DELETE: # if status in request == -1 (delete)
                if reaction_obj: # and user == comment.author: # if there is a reaction and user trying do delete his reaction
                    reaction_obj.delete()

                    # Update rating of the comment
                    comment.rating = comment._get_rating()
                    comment.save(update_fields=['rating'])

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
                return Response({'error': f'Поле status некорректно. status может принимать следующие значения: {self.get_str_reaction_choices()}'}, status=status.HTTP_400_BAD_REQUEST)
        
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