from django.urls import path, include
from rest_framework.routers import DefaultRouter

from blog import views


router = DefaultRouter()
router.register('tags', views.TagViewSet)
router.register('categories', views.CategoryViewSet)
router.register('posts', views.PostViewSet)

app_name = 'blog'

urlpatterns = [
    path('', include(router.urls))
]