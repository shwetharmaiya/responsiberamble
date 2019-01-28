import os
from django.db import models

from django.contrib.auth.models import User as Auth_User

from datetime import datetime
import ramble.settings as settings

# Create your models here.


class Profile(models.Model):
    user_id = models.ForeignKey(Auth_User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=50)
    profile_pic = models.ImageField(upload_to='profilepix/')
    bio = models.CharField(max_length=150)


class Post(models.Model):
    user_id = models.ForeignKey(Auth_User, on_delete=models.CASCADE)
    post_timestamp = models.DateTimeField(default=datetime.now)
    post_title = models.CharField(max_length=100)
    post_text = models.CharField(max_length=10000)


class Like(models.Model):
    class Meta:
        unique_together = (('user_id', 'post_id'),)
    user_id = models.ForeignKey(Auth_User, on_delete=models.CASCADE)
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)


class Share(models.Model):
    user_id = models.ForeignKey(Auth_User, on_delete=models.CASCADE)
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)


class Comment(models.Model):
    user_id = models.ForeignKey(Auth_User, on_delete=models.CASCADE)
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment_text = models.CharField(max_length=1000)


class Follow(models.Model):
    class Meta:
        unique_together = (('follower_id', 'followee_id'),)
    follower_id = models.ForeignKey(Auth_User, on_delete=models.CASCADE, related_name="followee_id")
    followee_id = models.ForeignKey(Auth_User, on_delete=models.CASCADE, related_name="follower_id")


