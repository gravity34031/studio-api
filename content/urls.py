from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from .views import *
from rest_framework.routers import DefaultRouter, SimpleRouter

router = DefaultRouter()
router.register(r'news', NewsViewSet, basename='news')



urlpatterns = [
    path('', include(router.urls)),
    path('youtube/', YoutubeListView.as_view()),
    path('youtube/<int:pk>/', YoutubeRetrieveView.as_view()),
]


"""
youtube/

    GET
    ?search='<title/description>'


    POST
    link - youtube video link
    This fields genereratin automaticly from link data. May be filled to change auto values:
        title
        image
    description - is not required 


    PATCH
    link

    This fields will generate automaticly and replaced IF it's in request and have value NULL or ''
    title 
    image
    
    description
"""
