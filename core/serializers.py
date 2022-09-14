from dataclasses import fields
from urllib import request
from rest_framework import serializers 
from django.contrib.auth.models import User 
from .models import  Like, Post, PostImages, Comment, Favorites, Followers







class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Followers 
        fields = ('post',)

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['post'] = PostListSerializer(instance.post).data
        return repr


class FavoritesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorites 
        fields = ('post',)

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['post'] = PostListSerializer(instance.post).data
        return repr



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password',)

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['favorites'] = FavoritesSerializer(instance.favorites.all(), many=True).data
        return repr

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['followers'] = FollowSerializer(instance.followers.all(), many=True).data
        return repr

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')



class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImages
        exclude = ('id',)

class CommentSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Comment
        fields = ('id', 'body', 'owner', 'post')

class PostSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    category = serializers.ReadOnlyField(source='category.name')
    images = PostImageSerializer(many=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = '__all__'
    
    def is_liked(self, post):
        user = self.context.get('request').user
        return user.liked.filter(post=post).exists()

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        user = self.context.get('request').user
        if user.is_authenticated:
            repr['is_liked'] = self.is_liked(instance)
        repr['likes_count'] = instance.likes.count()
        return repr


class PostListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post 
        fields = ('id', 'title', 'preview',)
    
    class Meta:
        model = Post 
        fields = '__all__'


class PostCreateSerializer(serializers.ModelSerializer):
    images = PostImageSerializer(many=True, read_only=False, required=False)

    class Meta:
        model = Post
        fields = ('title', 'body', 'preview', 'images',)

    def create(self, validated_data):
        request = self.context.get('request')
        created_post = Post.objects.create(**validated_data)
        images_data = request.FILES
        images_object = [PostImages(post=created_post, image=image) for image in images_data.getlist('images')]
        PostImages.objects.bulk_create(images_object)
        return created_post

class LikeSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    class Meta:
        model = Like
        fields = ('owner',)

