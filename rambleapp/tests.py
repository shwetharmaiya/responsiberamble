from django.test import TestCase

import datetime

from django.test import Client, TestCase
#from django.contrib.auth.models import User as Auth_User

from .models import Auth_User, Profile, Post, Like


# Create your tests here.

class ModelsTestCase(TestCase):
	
	def setUp(self):
		#Create User Profile
		u1 = Auth_User.objects.create(username="shwetha", password="shwetha", email="shwetha@example.com", first_name="Shwetha", last_name="Harsha")
		p1 = Profile.objects.create(user_id=u1, full_name="Harsha G",profile_pic="pics3", bio="Noob coder")
		
		#p2 = Profile.objects.create(user_id=5, full_name="Shwetha Harsha",profile_pic="pics4", bio="Noob coder 1")
		post1= Post.objects.create(user_id=u1, post_timestamp=datetime.datetime.now, post_title="Hello", post_text="Why do we use it?It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout. The point of using Lorem Ipsum is that it has a more-or-less normal distribution of letters, as opposed to using 'Content here, content here', making it look like readable English. Many desktop publishing packages and web page editors now use Lorem Ipsum as their default model text, and a search for 'lorem ipsum' will uncover many web sites still in their infancy. Various versions have evolved over the years, sometimes by accident, sometimes on purpose (injected humour and the like)", tags="Romance")

	def test_post_count(self):
		u1 = Auth_User.objects.create(username="shwetharm", password="shwetharm", email="shwetharm@example.com", first_name="ShwethaRM", last_name="HarshaRM")
		postSRM= Post.objects.create(user_id=u1, post_timestamp=datetime.datetime.now, post_title="Hello", post_text="Why do we use it?It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout. The point of using Lorem Ipsum is that it has a more-or-less normal distribution of letters, as opposed to using 'Content here, content here', making it look like readable English. Many desktop publishing packages and web page editors now use Lorem Ipsum as their default model text, and a search for 'lorem ipsum' will uncover many web sites still in their infancy. Various versions have evolved over the years, sometimes by accident, sometimes on purpose (injected humour and the like)", tags="Romance")

		a = Post.objects.get(user_id=u1)
		self.assertEqual(Post.objects.filter(user_id=u1).count(), 1)

	def test_like_count(self):	
		u1 = Auth_User.objects.create(username="HarshaG", password="harshag", email="harshag@example.com", first_name="Harsha", last_name="Gurumurthy")
		post2 = Post.objects.create(user_id=u1, post_timestamp=datetime.datetime.now, post_title="Hi", post_text="Why do we use it?It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout. The point of using Lorem Ipsum is that it has a more-or-less normal distribution of letters, as opposed to using 'Content here, content here', making it look like readable English. Many desktop publishing packages and web page editors now use Lorem Ipsum as their default model text, and a search for 'lorem ipsum' will uncover many web sites still in their infancy. Various versions have evolved over the years, sometimes by accident, sometimes on purpose (injected humour and the like)", tags="abcd")
		l = Like.objects.create(user_id=u1, post_id=post2)
		self.assertEqual(Like.objects.filter(user_id=u1).count(), 1	)