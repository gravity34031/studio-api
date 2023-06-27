from django.shortcuts import render
from django.http import QueryDict
from django.db.models import Count, F, Prefetch
from django.shortcuts import get_object_or_404
from .models import *
from .serializers import *
from core.models import Title
from comments.models import Comment
from core.serializers import RatingSerializer
from core.views import TitleListView
from rest_framework import viewsets, permissions, status, generics
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response


from django.contrib.auth import get_user_model
User = get_user_model()

from rest_framework.filters import SearchFilter
from core.custom_moduls.paginators import CommentSetPagination

from core.custom_moduls.image_management import deleteImage
# Create your views here.



class RegisterView(APIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        data = request.data
        # data = request.data.copy() # CHANGE CHANGE CHANGE CHANGE CHANGE CHANGE CHANGE CHANGE 
        # data['username'] = time.time() # CHANGE CHANGE CHANGE CHANGE CHANGE CHANGE CHANGE CHANGE
        # print(data) 
        serializer = RegisterSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)



class GetProfileView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'username'



class ProfileView(APIView):
    queryset = User.objects.all()
    serializer_class = ChangeProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        data = request.data
        user = request.user
        profile = get_object_or_404(User, username=user.username)

        if data:
            serializer = self.serializer_class(instance=profile, data=data, partial=True, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data)
        return Response(status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        password = request.data.get('password')
        user = request.user
        profile = get_object_or_404(User, username=user.username)

        # if password in request is user password
        if profile.check_password(password):
            avatar = profile.avatar
            profile.delete()
            deleteImage(avatar)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'Пароль неверный или его нет в запросе'}, status=status.HTTP_403_FORBIDDEN)



class ChangePasswordView(GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"detail": "Пароль успешно изменен!"}, status=status.HTTP_200_OK)



class FavouriteTitlesView(TitleListView):
    permission_classes = [permissions.AllowAny]

    def filter_queryset(self, queryset):
        username = self.kwargs.get('username')
        return super().filter_queryset(queryset.filter(favourites__username=username))



class RatingTitlesView(TitleListView):
    permission_classes = [permissions.AllowAny]
    
    def filter_queryset(self, queryset):
        username = self.kwargs.get('username')
        return super().filter_queryset(queryset.filter(title_rating__user__username=username))

    def get_list_serializer(self, *args, **kwargs):
        # change serializer to which has field 'your_rating'
        return RatedTitlesSerializer(*args, **kwargs)



class CommentsView(generics.ListAPIView):
    serializer_class = CommentSerializer
    pagination_class = CommentSetPagination
    filter_backends = [SearchFilter]
    search_fields = ['body']
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        username = self.kwargs.get('username')
        return Comment.objects.select_related('author').prefetch_related('content_object')\
            .filter(author__username=username).order_by('-create_time')



# after register need login user automaticly