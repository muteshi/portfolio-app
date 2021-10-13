from django.urls import path, include
from rest_framework.routers import DefaultRouter

from blog import views


router = DefaultRouter()
router.register('tags', views.TagViewSet)
router.register('categories', views.CategoryViewSet)
# router.register('recipes', views.RecipeViewSet)

app_name = 'blog'

urlpatterns = [
    path('', include(router.urls))
]