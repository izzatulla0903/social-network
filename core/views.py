from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from rest_framework import generics, permissions
from rest_framework.filters import SearchFilter

from account.models import CustomUser

from .permissions import IsAccountOwner, IsAuthor
from . import serializers
from .models import  Post, Comment, Like, Favorites, Followers
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination




class StandartResultsPagination(PageNumberPagination): #-stranisy
    page_size = 3
    page_query_param = 'page'
    max_page_size = 1000


class UserListView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = (serializers.UserListSerializer)
    filter_backends = (SearchFilter,)
    search_fields = (User,)

class UserDetailView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = (permissions.IsAuthenticated, IsAccountOwner)
    serializer_class = serializers.UserSerializer
    


class PostViewSet(ModelViewSet):
    queryset = Post.objects.select_related('owner')
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_fields = ('owner',)
    search_fields = ('title',)
    pagination_class = StandartResultsPagination
    

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_serializer_class(self):
        if self.action in ('retrieve',):
            return serializers.PostSerializer
        elif self.action in ('create', 'update', 'partial_update'):
            return serializers.PostCreateSerializer
        else:
            return serializers.PostListSerializer
    
    def get_permissions(self):
        if self.action in ('create', 'add_to_liked', 'remove_from_liked', 'favorite_action', 'followers_action'):
            return [permissions.IsAuthenticated()]
        elif self.action in ('update', 'partial_update', 'destroy', 'get_likes'):
            return [permissions.IsAuthenticated(), IsAuthor()]
        else:
            return [permissions.AllowAny(),] 


    # api/v1/posts/<id>/comments/
    @action(['GET'], detail=True)
    def comments(self, request, pk):
        post = self.get_object()
        comments = post.comments.all()
        serializer = serializers.CommentSerializer(comments, many=True)
        return Response(serializer.data, status=200)

    #api/v1/posts/<id>/add_to_liked/
    @action(['POST'], detail=True)
    def add_to_liked(self, request, pk):
        post = self.get_object()
        if request.user.liked.filter(post=post).exists():
            return Response('Вы уже лайкали этот пост', status=400)
        Like.objects.create(post=post, owner=request.user)
        return Response('Вы поставили лайк!', status=201)
    # api/v1/posts/<id>/remove_from_liked/
    @action(['POST'], detail=True)
    def remove_from_liked(self, request, pk):
        post = self.get_object()
        if not request.user.liked.filter(post=post).exists():
            return Response('Вы не лайкали этот пост!', status=400)
        request.user.liked.filter(post=post).delete()
        return Response('Ваш лайк удален!', status=204)
    
    #api/v1/posts/<id>/get_likes/
    @action(['GET'], detail=True)
    def get_likes(self, request, pk):
        post = self.get_object()
        likes = post.likes.all()
        serializer = serializers.LikeSerializer(likes, many=True)
        return Response (serializer.data, status=200)

    #api/v1/posts/<id>/favorite_action
    @action(['POST'], detail=True)
    def favorite_action(self, request, pk):
        post = self.get_object()
        if request.user.favorites.filter(post=post).exists():
            request.user.favorites.filter(post=post).delete()
            return Response('Убрали из избранных', status=204)
        Favorites.objects.create(post=post, owner=request.user)
        return Response('Добавлено в избранное!', status=201)

    #api/v1/posts/<id>/follow_action
    @action(['POST'], detail=True)
    def followers_action(self, request, pk):
        post = self.get_object()
        if request.user.followers.filter(post=post).exists():
            request.user.followers.filter(post=post).delete()
            return Response('Вы подписались', status=204)
        Followers.objects.create(post=post, owner=request.user)
        return Response('Вы убрали подписку!', status=201)




class CommentListView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsAuthor)


    
