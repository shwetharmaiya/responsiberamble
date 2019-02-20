from django.shortcuts import redirect

# Create your views here.
from django.http import HttpResponse, HttpResponseForbidden
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout

from social_django.models import UserSocialAuth

from .models import Post, Like, Follow, Profile, InterestedUsers
from .forms import ProfileForm
from django.contrib.auth.models import User as Auth_User

# Pages

def landing_page(request):
    template = loader.get_template('rambleapp/landing_page.html')
    context = {}
    return HttpResponse(template.render(context, request))

def post_email(request):
    if request.POST:
        email = request.POST['email']
        try:
            emailobj = InterestedUsers.objects.get(email_id=email)
        except InterestedUsers.DoesNotExist:
            new_interested_user = InterestedUsers(email_id=email)
            new_interested_user.save()
        return HttpResponse(204)
    return HttpResponseForbidden("Allowed Only Via Post")

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
    posts_and_likes = [(post, len(Like.objects.filter(post_id=post))) for post in posts]

    user_liked_posts = set([like.post_id.id for like in Like.objects.filter(user_id=user)])
    user_followers = set([follow.followee_id.id for follow in Follow.objects.filter(follower_id=user)])
    context = {'posts': posts, 'user_liked_posts': user_liked_posts,
               'user_followers': user_followers, 'user_profile': user_profile,
               'posts_and_likes': posts_and_likes}
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

# user profile helper methods: 

def twitter_user_context(request_obj):
    context = {}
    try:
        twitter_login = request_obj.user.social_auth.get(provider='twitter')
    except UserSocialAuth.DoesNotExist:
        twitter_login = None
    except AttributeError:
        twitter_login = None
    if twitter_login:
        user = Auth_User.objects.get(pk=request_obj.user.id)
        user_profile = Profile.objects.get(user_id=request_obj.user.id)
        user_followers = set([follow.followee_id.id for follow in Follow.objects.filter(follower_id=user)])
        user_liked_posts = set([like.post_id.id for like in Like.objects.filter(user_id=user)])

        context['user_liked_posts'] = user_liked_posts
        context['user_followers'] = user_followers
        context['user_profile'] = user_profile
    return context 


def get_user_profile(request, user_id):
    try:
        profile_user = Auth_User.objects.get(pk=user_id)
    except Auth_User.DoesNotExist:
        profile_user = None
    if profile_user:
        user_posts = Post.objects.filter(user_id=profile_user).order_by('-post_timestamp')
        user_posts_and_likes = [(post, len(Like.objects.filter(post_id=post))) for post in user_posts]
        profile_user_profile = Profile.objects.get(user_id=request.user.id)

        profile_context = {'profile_user': profile_user, 'posts': user_posts,
                   'posts_and_likes': user_posts_and_likes,
                   'profile_user_profile': profile_user_profile,
                    }
    else:
        profile_context = {}

    loggedin_user_context = twitter_user_context(request)

    context = {**profile_context, **loggedin_user_context}

    template = loader.get_template('rambleapp/user_posts.html')
    return HttpResponse(template.render(context, request))


def get_user_profile_likes(request, user_id):
    try:
        profile_user = Auth_User.objects.get(pk=user_id)
    except Auth_User.DoesNotExist:
        profile_user = None
    if profile_user:
        profile_user_profile = Profile.objects.get(user_id=request.user.id)
        profile_user_likes = [like.post_id for like in Like.objects.filter(user_id=profile_user)]
        profile_user_posts_and_likes = [(post, len(Like.objects.filter(post_id=post))) for post in profile_user_likes]


        profile_context = {'profile_user': profile_user, 
                   'profile_user_profile': profile_user_profile,
                   'profile_user_likes': profile_user_likes,
                   'profile_user_posts_and_likes': profile_user_posts_and_likes,
                    }
    else:
        profile_context = {}

    loggedin_user_context = twitter_user_context(request)

    context = {**profile_context, **loggedin_user_context}

    template = loader.get_template('rambleapp/user_likes.html')
    return HttpResponse(template.render(context, request))


def get_user_profile_follows(request, user_id):
    try:
        profile_user = Auth_User.objects.get(pk=user_id)
    except Auth_User.DoesNotExist:
        profile_user = None
    if profile_user:
        profile_user_follows = [follow.followee_id for follow in Follow.objects.filter(follower_id=profile_user)]
        follows_profiles = Profile.objects.all().filter(user_id__in=profile_user_follows)
        profile_user_profile = Profile.objects.get(user_id=profile_user)

        profile_context = {'profile_user': profile_user,
                   'profile_user_profile': profile_user_profile,
                   'follows_profiles': follows_profiles,
                    }
    else:
        profile_context = {}

    loggedin_user_context = twitter_user_context(request)

    context = {**profile_context, **loggedin_user_context}

    template = loader.get_template('rambleapp/user_follows.html')
    return HttpResponse(template.render(context, request))


def get_user_profile_followers(request, user_id):
    try:
        profile_user = Auth_User.objects.get(pk=user_id)
    except Auth_User.DoesNotExist:
        profile_user = None
    if profile_user:
        profile_user_followers = [follow.follower_id for follow in Follow.objects.filter(followee_id=profile_user)]
        followers_profiles = Profile.objects.all().filter(user_id__in=profile_user_followers)
        profile_user_profile = Profile.objects.get(user_id=profile_user)

        print("num followers", len(profile_user_followers))
        print("num follower profiles", len(followers_profiles))

        profile_context = {'profile_user': profile_user,
                   'profile_user_profile': profile_user_profile,
                   'followers_profiles': followers_profiles,
                    }
    else:
        profile_context = {}

    loggedin_user_context = twitter_user_context(request)

    context = {**profile_context, **loggedin_user_context}

    template = loader.get_template('rambleapp/user_followers.html')
    return HttpResponse(template.render(context, request))


def get_ramblepost(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
        post_likes = len(Like.objects.filter(post_id=post))
        context = {'post': post, 'num_likes': post_likes, }

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

def get_tagpage(request, tag_page):
     posts = Post.objects.filter(tags__name__in=[tag_page])
     posts_and_likes = [(post, len(Like.objects.filter(post_id=post))) for post in posts]
     context = {'posts': posts, 'posts_and_likes': posts_and_likes, 'tag': tag_page}

     template = loader.get_template('rambleapp/tag_page.html')
     return HttpResponse(template.render(context, request))

def likes_get(request, post_id):
    post = Post.objects.get(pk=post_id)
    users_who_liked = [user.user_id for user in Like.objects.filter(post_id=post)]
    users_who_liked_profiles = Profile.objects.all().filter(user_id__in=users_who_liked)
    template = loader.get_template('rambleapp/display_liked_users.html')
    context = {'users': users_who_liked_profiles}
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
    posts_and_likes = [(post, len(Like.objects.filter(post_id=post))) for post in posts]

    context = {'twitter_login': twitter_login, 'posts': posts, 'posts_and_likes': posts_and_likes}
    return HttpResponse(template.render(context, request))


def logout(request):
    auth_logout(request)
    return redirect('index')


# Post Methods


@login_required
def post_ramble(request):
    post_text = request.POST['new_ramble_post']
    # process post text 
    BLANK_LINE = '<p>&nbsp;</p>'
    broken_lines = post_text.split(BLANK_LINE)
    broken_lines = [line for line in broken_lines if not line.isspace() and line != '' ]

    post_text = BLANK_LINE.join(broken_lines)

    post_title = request.POST['new_ramble_title']
    post_tags = request.POST['new_ramble_tags']
    if not post_tags:
        post_tags = 'uncategorized, other random stuff'
    user = Auth_User.objects.get(pk=request.user.id)

    new_post = Post(user_id=user, post_text=post_text, post_title=post_title)
    new_post.save()
    # This is a many to many model, so you need to save it first, 
    # so it has a primary key
    # then you add tags to it using the add method. 
    # and save it again. 
    tagslist = [str(r).strip() for r in post_tags.split(',')]

    new_post.tags.add(*tagslist)
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
