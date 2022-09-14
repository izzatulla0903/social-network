from distutils.command.upload import upload
from pickle import TRUE
from django.db import models
from tabnanny import verbose
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Post(models.Model):
    title = models.CharField(max_length=255, unique=True, verbose_name='Название')
    body = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    preview = models.ImageField(upload_to='images/', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'{self.owner} - {self.title}'

    class Meta:
        ordering = ('created_at',)
        verbose_name = 'Посты'
        verbose_name_plural = 'Пост'

class PostImages(models.Model):
    title = models.CharField(max_length=150, blank=True)
    image = models.ImageField(upload_to='images/')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')

    @staticmethod
    def generate_name():
        from random import randint
        return 'image' + str(randint(100000, 999999))
    
    def save(self, *args, **kwargs):
        self.title = self.generate_name()
        return super(PostImages, self).save(*args, **kwargs)

class Comment(models.Model):
    owner = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.owner} -> {self.post} -> {self.created_at}'

class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked')

    class Meta:
        unique_together = ['post', 'owner']


class Favorites(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='favorites')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')

    class Meta:
        unique_together = ['post', 'owner']


class Followers(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='followers')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')

    class Meta:
        unique_together = ['post', 'owner']





