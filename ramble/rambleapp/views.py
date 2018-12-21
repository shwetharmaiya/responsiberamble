from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
  template = loader.get_template('rambleapp/index.html')
  context = {'latest_question_list': "fuckin 404", }
  return HttpResponse(template.render(context, request))

def user_profile(request, user_id):
  return HttpResponse("This is a user profile page!")

def login(request):
  template = loader.get_template('rambleapp/login.html')
  context = {'latest_question_list': "fuckin 404", }
  return HttpResponse(template.render(context, request))

def post(request, post_id):
  return HttpResponse("This is a post page!")
