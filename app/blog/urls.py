from django.urls import path, include
from rest_framework.routers import DefaultRouter

from blog import views


router = DefaultRouter()
router.register('tags', views.TagViewSet)
router.register('categories', views.CategoryViewSet)
router.register('posts', views.PostViewSet)
router.register('portfolios', views.PortfolioViewSet)
router.register('resumes', views.ResumeViewSet)
router.register('skills', views.SkillViewSet)
# router.register('messages', views.MessageViewSet)

app_name = 'blog'

urlpatterns = [
    path('', include(router.urls)),
     path('new-message/',  views.MessageCreateAPIView.as_view(), name='message-create'),

]
