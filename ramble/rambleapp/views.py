from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse


def index(request):
  return HttpResponse("Hello, world. Welcome to Ramble!")

def user_profile(request, user_id):
  return HttpResponse("This is a user profile page!")

def login(request):
  return HttpResponse("This is a login page!")

def post(request, post_id):
  return HttpResponse("This is a post page!")
