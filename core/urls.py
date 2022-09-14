from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('posts', views.PostViewSet, basename='Post')

    

urlpatterns = [
    path('', include(router.urls)),
    path('comments/', views.CommentListView.as_view()),
    path('comments/<int:pk>/', views.CommentDetailView.as_view()),
    

]