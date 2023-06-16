import os, shutil
from django.conf import settings
from django.shortcuts import render
from django.http import QueryDict
from django.db.models import Count, F, Prefetch
from .models import *
from django.shortcuts import get_object_or_404
from .serializers import *
from rest_framework import viewsets, permissions, status, generics
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.settings import api_settings

from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from django.contrib.auth import get_user_model
User = get_user_model()
# Create your views here.

from .custom_moduls.paginators import TitleSetPagination
from .custom_moduls.filters import TitleFilter

from .custom_moduls.view_func import create_frames, pop_frames_from_data, get_client_ip
from .custom_moduls.image_management import deleteTitleFolder, deleteFramesFolder, deleteImage, deleteImgAndThumb



class StudioViewSet(viewsets.ModelViewSet):
    queryset = Studio.objects.all()
    serializer_class = StudioSerializer
    lookup_field = 'slug'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        photo, photo_thumbnail = instance.photo, instance.photo_thumbnail
        error = deleteImgAndThumb(photo, photo_thumbnail)

        self.perform_destroy(instance)
        return Response(error, status=status.HTTP_204_NO_CONTENT)

class TitleByStudioView(APIView):
    def get_queryset(self):
        return Title.objects.select_related('average_rating').prefetch_related('genres', 'title_views')

    def get(self, request, slug, *args, **kwargs):
        titles = self.get_queryset().filter(studios__slug=slug).order_by('-average_rating__rating', 'title') # order 
        serializer = TitleListSerializer(titles, many=True, context={'request': request})
        return Response(serializer.data)



class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    lookup_field = 'slug'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        photo, photo_thumbnail = instance.photo, instance.photo_thumbnail
        error = deleteImgAndThumb(photo, photo_thumbnail)

        self.perform_destroy(instance)
        return Response(error, status=status.HTTP_204_NO_CONTENT)

class TitleByActorView(APIView):
    def get_queryset(self):
        return TitleByStudioView.get_queryset(self)

    def get(self, request, slug, *args, **kwargs):
        titles = self.get_queryset().filter(actors__slug=slug).order_by('-average_rating__rating', 'title') # order 
        serializer = TitleListSerializer(titles, many=True, context={'request': request})
        return Response(serializer.data)



class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'slug'

class TitleByGenreView(APIView):
    def get_queryset(self):
        return TitleByStudioView.get_queryset(self)

    def get(self, request, slug, *args, **kwargs):
        titles = self.get_queryset().filter(genres__slug=slug).order_by('-average_rating__rating', 'title') # order 
        serializer = TitleListSerializer(titles, many=True, context={'request': request})
        return Response(serializer.data)



class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all().select_related('title', 'title__average_rating').prefetch_related('title__genres')
    serializer_class = ScheduleGetSerializer
    lookup_field = 'pk'

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return SchedulePostSerializer
        return self.serializer_class



########################################
#              TITLES                  #
########################################
class TitleListView(GenericAPIView):
    serializer_class = TitlePostSerializer # need for post request form in BrowsableAPIRenderer
    pagination_class = TitleSetPagination
    filter_backends = [OrderingFilter, SearchFilter, DjangoFilterBackend]
    filterset_class = TitleFilter
    search_fields = [
        'title', 'original_title', 'alternative_title__title', 'slug', 
        'related_lists__title', 'related_lists__alternative_title__title', 'related_lists__original_title'
    ]
    ordering_fields = ('create_time', 'update_time', 'title', 'aired_on', 'rating', 'popular')
    ordering = ['create_time'] # default sorting


    def get_queryset(self, *args, **kwargs):
        return Title.objects.select_related('average_rating').prefetch_related('genres', 'title_views') \
            .annotate(rating=F('average_rating__rating')) \
            .annotate(popular=Count(F('title_views'))) \
            

    def get_list_serializer(self, *args, **kwargs):
        return TitleListSerializer(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = {'request': request}
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_list_serializer(page, many=True, context=context)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_list_serializer(queryset, many=True, context=context)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        data, frames = pop_frames_from_data(request.data)
        auto_related_list = data.get('auto_related_list')

        title_serializer = TitlePostSerializer(data=data, context={'request': request, 'auto_related': auto_related_list})
        title_serializer.is_valid(raise_exception=True)
        title = title_serializer.save()

        create_frames(title, frames)

        return Response(title_serializer.data)


class TitleRetrieveView(APIView):
    serializer_class = TitlePostSerializer # need for patch request form in BrowsableAPIRenderer

    def get_queryset(self, *args, **kwargs):
        return Title.objects.select_related('average_rating').prefetch_related('title_views', 'related_lists__genres', 'related_lists__actors', 'related_lists__studios', 'related_lists__average_rating')

    def get(self, request, slug, *args, **kwargs):

        post = get_object_or_404(self.get_queryset(), slug=slug)
        serializer = TitleGetSerializer(post, context={'request': request})
        
        # add view & check if the ip doesn't see title yet
        ip = get_client_ip(request)
        TitleViews.objects.get_or_create(ip=ip, title=post)

        return Response(serializer.data)

    def patch(self, request, slug, *args, **kwargs):
        data, frames = pop_frames_from_data(request.data)
        auto_related_list = data.get('auto_related_list')

        instance = get_object_or_404(Title, slug=slug)
        serializer = TitlePostSerializer(instance=instance, data=data, partial=True, context={'request': request, 'auto_related': auto_related_list})
        serializer.is_valid(raise_exception=True)

        # delete images if they had been changed
        title_poster = instance.poster
        title_poster_thumb = instance.poster_thumbnail
        if title_poster:
            # del poster
            poster = data.get('poster', None)
            if poster:
                poster_path = os.path.join(str(title_poster))
                deleteImage(poster_path)
                # del poster thumbnail
                poster_thumb_path = os.path.join(str(title_poster_thumb))
                deleteImage(poster_thumb_path)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, slug , *args, **kwargs):
        instance = get_object_or_404(Title, slug=slug)
        # delete image folder
        error = deleteTitleFolder(instance)

        instance.delete()
        return Response(error, status=status.HTTP_204_NO_CONTENT)



class RandomTitleView(APIView):
    def get_queryset(self, *args, **kwargs):
        return TitleRetrieveView.get_queryset(self)

    def get(self, request, *args, **kwargs):
        from random import choice
        titles = Title.objects.values_list('pk', flat=True)
        random_title_pk = choice(titles)
        queryset = self.get_queryset()
        random_title = queryset.get(pk=random_title_pk)
        serializer = TitleGetSerializer(random_title, context={'request': request})
        return Response(serializer.data)


########################################
#              FRAMES                  #
########################################
class FramePostView(generics.CreateAPIView):
    queryset = Frame.objects.all()
    serializer_class = FrameSerializer


class FrameDeleteView(APIView):
    queryset = Frame.objects.all()
    serializer_class = FrameSerializer

    def delete(self, request, pk, *args, **kwargs):
        instance = get_object_or_404(Frame, pk=pk)

        image, image_thumbnail = instance.image, instance.image_thumbnail
        error = deleteImgAndThumb(image, image_thumbnail)
            
        instance.delete()
        return Response(error, status=status.HTTP_204_NO_CONTENT)


class FramesDeleteView(APIView):
    queryset = Frame.objects.all()
    serializer_class = FrameSerializer

    # delete all frames of title
    def delete(self, request, slug, *args, **kwargs):
        frames = Frame.objects.filter(title__slug=slug)
        if len(frames) > 0:
            error = deleteFramesFolder(frames[0].img_path)

            frames.delete()
            return Response(error, status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


########################################
#              RATING                  #
########################################
class RatingListView(APIView):
    serializer_class = RatingSerializer

    def get_queryset(self, *args, **kwargs):
        return TitleRating.objects.select_related('average_rating')

    # def get(self, request, *args, **kwargs): # get titles sorted by rating
    #     titles = Title.objects.all().order_by('-average_rating__rating', 'title')
    #     serializer = TitleGetSerializer(titles, many=True, context={'request': request})
    #     return Response(serializer.data)

    def patch(self, request, *args, **kwargs): 
        data = request.data
        user = request.user
        title_data = data.get('title', None)
        if title_data:
            title_queryset = Title.objects.select_related('average_rating')
            title = get_object_or_404(title_queryset, slug=title_data)
        if user and title: # check if user left rating and find instance of it
            rating_instance = TitleRating.objects.filter(title=title, user=user).first()
        if rating_instance: # user left rating: Change it (update)
            if str(rating_instance.rating) == str(data.get('rating')):
                return Response(status=status.HTTP_400_BAD_REQUEST)
            serializer = self.serializer_class(data=data, instance=rating_instance, partial=True, context={'request': request}) # request in context is NECESSARY
            serializer.is_valid(raise_exception=True)
            serializer.save()
        else: # create rating (post)
            serializer = self.serializer_class(data=data, context={'request': request}) # request in context is NECESSARY for current user default
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data)

class RatingDeleteView(APIView):
    serializer_class = RatingSerializer

    def get_queryset(self, *args, **kwargs):
        return TitleRating.objects.all()
    
    def delete(self, request, slug, *args, **kwargs):
        user = request.user
        if user:
            title = get_object_or_404(Title, slug=slug)
            rating_instance = TitleRating.objects.filter(title=title, user=user).first()
            rating_instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)



class FavouriteView(APIView):
    def get_queryset(self, *args, **kwargs):
        return Title.objects.filter(favourites=self.request.user)

    def patch(self, request, slug, *args, **kwargs):
        data = request.data
        user = request.user

        if user:
            title = get_object_or_404(Title, slug=slug)
            if user in title.favourites.all(): # if user user added title to favourite
                title.favourites.remove(user) # delete from favourite
                return Response({'data': 'Убрано из избранного'}, status=status.HTTP_204_NO_CONTENT)
            title.favourites.add(user) # else add to favourite
            return Response({'data': 'Добавлено в избранное'}, status=status.HTTP_200_OK)
        return Response({'data': 'Добавлять в избранное могут только авторизованные пользователи'}, status=status.HTTP_401_UNAUTHORIZED)













#RECOMENDATION SYSTEM






   ###   ###    #########    ###          #######
   ###   ###    #########    ###          ###   ###
   ###   ###    ###          ###          ###    ###
   #########    #########    ###          ###   ###
   #########    #########    ###          #######
   ###   ###    ###          ###          ###
   ###   ###    #########    #########    ###
   ###   ###    #########    #########    ###


#    |||   |||    |||||||||    |||          |||||||
#    |||   |||    |||||||||    |||          |||   |||
#    |||   |||    |||          |||          |||    |||
#    |||||||||    |||||||||    |||          |||   |||
#    |||||||||    |||||||||    |||          |||||||
#    |||   |||    |||          |||          |||
#    |||   |||    |||||||||    |||||||||    |||
#    |||   |||    |||||||||    |||||||||    |||


#    ///   ///    /////////    ///          ///////
#    ///   ///    /////////    ///          ///   ///
#    ///   ///    ///          ///          ///    ///
#    /////////    /////////    ///          ///   ///
#    /////////    /////////    ///          ///////
#    ///   ///    ///          ///          ///
#    ///   ///    /////////    /////////    ///
#    ///   ///    /////////    /////////    ///


#    ***   ***    *********    ***          *******
#    ***   ***    *********    ***          ***   ***
#    ***   ***    ***          ***          ***    ***
#    *********    *********    ***          ***   ***
#    *********    *********    ***          *******
#    ***   ***    ***          ***          ***
#    ***   ***    *********    *********    ***
#    ***   ***    *********    *********    ***