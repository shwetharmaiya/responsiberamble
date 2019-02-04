from django.urls import path
import social_django
from . import views
from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
  path('', views.index, name='index'),
  # path('accounts/profile/', views.index, name='index'),
  path('u/<int:user_id>', views.get_user_profile, name='user_profile'),
  path('post/<int:post_id>', views.get_ramblepost, name='post'),
  path('ramblepost', views.post_ramble, name='post_a_ramble'),
  path('deletepost', views.delete_post, name='delete_a_ramble'),
  path('likepost', views.like_post, name='like_a_ramble'),
  path('followuser', views.follow_user, name='follow_a_user'),
  path('make_profile', views.make_profile, name='edit_your_profile'),
  path('post_profile', views.post_profile, name='post_profile'),
  path('login', views.login, name='login'),
  path('logout', views.logout, name='logout'),
  # path('accounts/login/', views.login, name='sociallogin'),
  url(r'^oauth/', include('social_django.urls', namespace='social')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

