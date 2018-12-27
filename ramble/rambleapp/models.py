from django.db import models

from django.contrib.auth.models import User as Auth_User

from datetime import datetime

# Create your models here.

class Post(models.Model):
  user_id = models.ForeignKey(Auth_User, on_delete=models.CASCADE)
  post_timestamp = models.DateTimeField(default=datetime.now)
  post_text = models.CharField(max_length=10000)


class Like(models.Model):
  user_id = models.ForeignKey(Auth_User, on_delete=models.CASCADE)
  post_id = models.ForeignKey(Post, on_delete=models.CASCADE)


class Share(models.Model):
  user_id = models.ForeignKey(Auth_User, on_delete=models.CASCADE)
  post_id = models.ForeignKey(Post, on_delete=models.CASCADE)


class Comment(models.Model):
  user_id = models.ForeignKey(Auth_User, on_delete=models.CASCADE)
  post_id = models.ForeignKey(Post, on_delete=models.CASCADE)
  comment_text = models.CharField(max_length=1000)
