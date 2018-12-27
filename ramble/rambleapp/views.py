from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect

from social_django.models import UserSocialAuth


@login_required
def index(request):
  template = loader.get_template('rambleapp/index.html')
  context = {}
  return HttpResponse(template.render(context, request))

def user_profile(request, user_id):
  return HttpResponse("This is a user profile page!")

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
  return HttpResponse("This is a post page!")


