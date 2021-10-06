from django.urls import path

from . import views

app_name = 'user'


urlpatterns = [
    path('user-create/', views.CreateUserAccountView.as_view(),
         name='user-create'),
    path('user-token/', views.CreateTokenView.as_view(),
         name='user-token'),
    path('user-manage/', views.ManageUserAccountView.as_view(),
         name='user-manage')
]