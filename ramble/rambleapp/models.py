from django.db import models

# Create your models here.

class User(models.Model):
  user_name = models.CharField(max_length=16)

class Post(models.Model):
  user_id = models.ForeignKey(User, on_delete=models.CASCADE)
  post_timestamp = models.DateTimeField('date published')
  post_text = models.CharField(max_length=10000)

class Like(models.Model):
  user_id = models.ForeignKey(User, on_delete=models.CASCADE)
  post_id = models.ForeignKey(Post, on_delete=models.CASCADE)

class Share(models.Model):
  user_id = models.ForeignKey(User, on_delete=models.CASCADE)
  post_id = models.ForeignKey(Post, on_delete=models.CASCADE)

