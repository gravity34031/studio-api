from django.conf import settings
from django.shortcuts import render
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

from core.custom_moduls.image_management import deleteImage
from core.custom_moduls.view_func import get_client_ip
from core.custom_moduls.paginators import YoutubeSetPagination, NewsSetPagination
from core.custom_moduls.permissions import IsAdminOrReadOnly

# from .custom_moduls.filters import

class NewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    pagination_class = NewsSetPagination
    filter_backends = [SearchFilter]
    search_fields = ['title', 'body']
    lookup_field = 'slug'
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return News.objects.select_related('author')\
            .annotate(views_count=Count(F('news_views')))\
            .order_by('-create_time')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        # add views to the post
        ip = get_client_ip(request)
        content_type = ContentType.objects.get_for_model(News)
        Views.objects.only('pk').get_or_create(ip=ip, content_type=content_type, object_id=instance.pk)

        return Response(serializer.data)




class YoutubeListView(generics.ListCreateAPIView):
    queryset = YoutubePost.objects.all()
    serializer_class = YoutubeSerializer
    pagination_class = YoutubeSetPagination
    filter_backends = [SearchFilter]
    search_fields = ['title', 'description']
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return self.queryset.select_related('author').order_by('-create_time')



class YoutubeRetrieveView(generics.RetrieveUpdateDestroyAPIView):
    queryset = YoutubePost.objects.all()
    serializer_class = YoutubeSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return self.queryset.select_related('author')

    def delete(self, request, pk, *args, **kwargs):
        instance = get_object_or_404(YoutubePost, pk=pk)
        instance.delete()
        deleteImage(instance.image)
        return Response(status=status.HTTP_204_NO_CONTENT)
