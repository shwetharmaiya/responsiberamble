from django.urls import path
import social_django
from . import views
from django.conf.urls import url, include

urlpatterns = [
  path('', views.index, name='index'),
  # path('accounts/profile/', views.index, name='index'),
  path('u/<int:user_id>', views.user_profile, name='user_profile'),
  path('post/<int:post_id>', views.post, name='post'),
  path('ramblepost', views.post_ramble, name='post_a_ramble'),
  path('login', views.login, name='login'),
  path('logout', views.logout, name='logout'),
  # path('accounts/login/', views.login, name='sociallogin'),
  url(r'^oauth/', include('social_django.urls', namespace='social')),
]
