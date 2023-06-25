from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from .views import *


urlpatterns = [
    path('auth/', include('rest_framework.urls')),
    path('register/', RegisterView.as_view()),
    path('change-password/', ChangePasswordView.as_view()),
    path('profile/', ProfileView.as_view()),
    path('profile/<str:username>/', GetProfileView.as_view()),
    path('profile/<str:username>/favourite/', FavouriteTitlesView.as_view()),
    path('profile/<str:username>/rating/', RatingTitlesView.as_view()),
    path('profile/<str:username>/comment/', CommentsView.as_view()),
]

"""
profile/

PATCH
    sex:-1 - None
         0 - female
         1 - male
    avatar: to auto-create-avatar need send NULL in request

DELETE
    password





change-password/

PUT 
    old_password
    new_password
    new_password2
"""