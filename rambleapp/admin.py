from django.contrib import admin
from .models import Auth_User, Profile, Post

# Register your models here.
#admin.site.register(Auth_User)
admin.site.register(Profile)
admin.site.register(Post)

