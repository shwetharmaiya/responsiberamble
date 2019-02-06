from django.shortcuts import redirect

# Create your views here.
from django.http import HttpResponse, HttpResponseForbidden
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout

from social_django.models import UserSocialAuth

from .models import Post, Like, Follow, Profile
from .forms import ProfileForm
from django.contrib.auth.models import User as Auth_User

# Pages

def landing_page(request):
    template = loader.get_template('rambleapp/landing_page.html')
    context = {}
    return HttpResponse(template.render(context, request))

@login_required
def index(request):
    user = Auth_User.objects.get(pk=request.user.id)
    try:
        user_profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        return redirect(make_profile)

    template = loader.get_template('rambleapp/index.html')

    # get all previous posts
    posts = Post.objects.all().order_by('-post_timestamp')

    user_liked_posts = set([like.post_id.id for like in Like.objects.filter(user_id=user)])
    user_followers = set([follow.followee_id.id for follow in Follow.objects.filter(follower_id=user)])
    context = {'posts': posts, 'user_liked_posts': user_liked_posts,
               'user_followers': user_followers, 'user_profile': user_profile}
    return HttpResponse(template.render(context, request))


@login_required
def make_profile(request):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
        return redirect(index)
    except Profile.DoesNotExist:
        form = ProfileForm(request.POST, request.FILES)
        template = loader.get_template('rambleapp/make_profile.html')
        context = {'form': form}
        return HttpResponse(template.render(context, request))


def get_user_profile(request, user_id):
    try:
        profile_user = Auth_User.objects.get(pk=user_id)
    except Auth_User.DoesNotExist:
        profile_user = None
    if profile_user:
        user_posts = Post.objects.filter(user_id=profile_user).order_by('-post_timestamp')
        profile_user_profile = Profile.objects.get(user_id=request.user.id)
        context = {'profile_user': profile_user, 'posts': user_posts,
                   'profile_user_profile': profile_user_profile}
    else:
        context = {}

    try:
        twitter_login = request.user.social_auth.get(provider='twitter')
    except UserSocialAuth.DoesNotExist:
        twitter_login = None
    except AttributeError:
        twitter_login = None
    if twitter_login:
        user = Auth_User.objects.get(pk=request.user.id)
        user_profile = Profile.objects.get(user_id=request.user.id)
        user_followers = set([follow.followee_id.id for follow in Follow.objects.filter(follower_id=user)])
        user_liked_posts = set([like.post_id.id for like in Like.objects.filter(user_id=user)])

        context['user_liked_posts'] = user_liked_posts
        context['user_followers'] = user_followers
        context['user_profile'] = user_profile

    template = loader.get_template('rambleapp/user.html')
    return HttpResponse(template.render(context, request))


def get_ramblepost(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
        context = {'post': post}
    except Post.DoesNotExist:
        post = None
        context = {}
    try:
        twitter_login = request.user.social_auth.get(provider='twitter')
    except UserSocialAuth.DoesNotExist:
        twitter_login = None
    except AttributeError:
        twitter_login = None
    if twitter_login:
        user = Auth_User.objects.get(pk=request.user.id)
        user_profile = Profile.objects.get(user_id=request.user.id)
        user_followers = set([follow.followee_id.id for follow in Follow.objects.filter(follower_id=user)])
        user_liked_posts = set([like.post_id.id for like in Like.objects.filter(user_id=user)])

        context['user_liked_posts'] = user_liked_posts
        context['user_followers'] = user_followers
        context['user_profile'] = user_profile

    template = loader.get_template('rambleapp/post.html')
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

    posts = Post.objects.all().order_by('-post_timestamp')

    context = {'twitter_login': twitter_login, 'posts': posts}
    return HttpResponse(template.render(context, request))


def logout(request):
    auth_logout(request)
    return redirect('index')


# Post Methods


@login_required
def post_ramble(request):
    post_text = request.POST['new_ramble_post']
    post_title = request.POST['new_ramble_title']
    user = Auth_User.objects.get(pk=request.user.id)
    new_post = Post(user_id=user, post_text=post_text, post_title=post_title)
    new_post.save()
    pk = new_post.pk
    # return HttpResponse(status=204)
    return HttpResponse(pk)


@login_required
def post_profile(request):
    print(request)
    if request.method == 'POST':
        print("Request method is post")
        user = Auth_User.objects.get(pk=request.user.id)
        form = ProfileForm(request.POST, request.FILES)
        print(form)
        if form.is_valid():
            new_profile = form.save(commit=False)
            new_profile.user_id = user
            # bio = form.cleaned_data['bio']
            # fullname = form.cleaned_data['fullname']
            # new_profile = Profile(user_id=user, profile_pic=pic, bio=bio, full_name=fullname)
            new_profile.save()
            return redirect('index')
        else:
            return HttpResponse("FUCK, form is invalid" + str(form.errors))
    return HttpResponseForbidden('allowed only via POST')


@login_required
def delete_post(request):
    user = Auth_User.objects.get(pk=request.user.id)
    post_id = request.POST['post_id']
    post = Post.objects.get(pk=post_id)
    if not post:
        return HttpResponse(status=400)
    if post.user_id == user:
        post.delete()
        return HttpResponse(status=204)
    else:
        return HttpResponse(status=400)


@login_required
def like_post(request):
    user_id = request.user.id
    user = None
    post = None
    try:
        user = Auth_User.objects.get(pk=user_id)
    except Auth_User.DoesNotExist:
        return HttpResponse(status=400)
    post_id = request.POST['post_id']
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return HttpResponse(status=400)

    if not user or not post:
        return HttpResponse(status=400)

    # check in like table if post is present
    try:
        like = Like.objects.get(user_id=user, post_id=post)
    except Like.DoesNotExist:
        # if not present, add new row with user id and post id
        new_like = Like(user_id=user, post_id=post)
        new_like.save()
        return HttpResponse(status=204)

    # if present, delete row
    like.delete()
    return HttpResponse(status=204)


@login_required
def follow_user(request):
    follower_id = request.user.id
    followee_id = request.POST['user_id']

    if follower_id == followee_id:
        return HttpResponse(status=400)

    try:
        follower = Auth_User.objects.get(pk=follower_id)
        followee = Auth_User.objects.get(pk=followee_id)
    except Follow.DoesNotExist:
        return HttpResponse(status=400)
    # check in followers table if the following relationship exists.
    try:
        followship = Follow.objects.get(follower_id=follower, followee_id=followee)
    except:
        # if it does, delete record.
        new_followship = Follow(follower_id=follower, followee_id=followee)
        new_followship.save()
        return HttpResponse(status=204)
    # If not, add relationship.
    followship.delete()
    return HttpResponse(204)
