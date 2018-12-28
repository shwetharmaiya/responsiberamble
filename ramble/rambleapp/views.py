from django.shortcuts import redirect

# Create your views here.
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout

from social_django.models import UserSocialAuth

from .models import Post
from django.contrib.auth.models import User as Auth_User


@login_required
def index(request):
  template = loader.get_template('rambleapp/index.html')

  # get all previous posts
  posts = Post.objects.all().order_by('post_timestamp')

  context = {'posts': posts}
  return HttpResponse(template.render(context, request))


@login_required
def post_ramble(request):
  post_text = request.POST['new_ramble_post']
  user = Auth_User.objects.get(pk=request.user.id)
  new_post = Post(user_id=user, post_text=post_text)
  new_post.save()
  return redirect('index')


def user_profile(request, user_id):
  try:
    profile_user = Auth_User.objects.get(pk=user_id)
  except Auth_User.DoesNotExist:
    profile_user = None
  if profile_user:
    user_posts = Post.objects.filter(user_id=profile_user)
    context = {'profile_user': profile_user, 'posts':user_posts}
  else:
    context = {}

  template = loader.get_template('rambleapp/user.html')
  return HttpResponse(template.render(context, request))


def login(request):
  user = request.user
  try:
    twitter_login = user.social_auth.get(provider='twitter')
  except UserSocialAuth.DoesNotExist:
    twitter_login = None
  except AttributeError:
    twitter_login = None
  template = loader.get_template('rambleapp/login.html')
  context = {'twitter_login': twitter_login, }
  return HttpResponse(template.render(context, request))


def logout(request):
  auth_logout(request)
  return redirect('index')


def post(request, post_id):
  try:
    post = Post.objects.get(pk=post_id)
  except Post.DoesNotExist:
    post = None
  context = {'post':post}

  template = loader.get_template('rambleapp/post.html')
  return HttpResponse(template.render(context, request))


