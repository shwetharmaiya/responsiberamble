from django.urls import path

from . import views

urlpatterns = [
  path('', views.index, name='index'),
  path('u/<int:user_id>', views.user_profile, name='user_profile'),
  path('post/<int:post_id>', views.post, name='post'), 
  path('login', views.login, name='login'),
]
