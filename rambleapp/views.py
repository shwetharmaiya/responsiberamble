import json 
from django.shortcuts import redirect

# Create your views here.
from django.http import HttpResponse, HttpResponseForbidden
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User as Auth_User

from social_django.models import UserSocialAuth

from .models import Post, Like, Follow, Profile, InterestedUsers, Comment, Collection, CollectionPost
from .forms import ProfileForm

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
    collection_posts = [post.post_id.pk for post in CollectionPost.objects.filter(collection_id__user_id=user)]

    context = {'posts': posts, 'user_liked_posts': user_liked_posts,
               'user_followers': user_followers, 'user_profile': user_profile,
               'posts_and_likes': posts_and_likes, 'user_collected_posts': collection_posts}
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

        collections = Collection.objects.filter(user_id=user)
        collection_posts = [post.post_id.pk for post in CollectionPost.objects.filter(collection_id__user_id=user)]

        context['user_liked_posts'] = user_liked_posts
        context['user_followers'] = user_followers
        context['user_profile'] = user_profile
        context['user_collected_posts'] = collection_posts
    return context 


def get_user_profile(request, user_id):
    try:
        profile_user = Auth_User.objects.get(pk=user_id)
    except Auth_User.DoesNotExist:
        profile_user = None
    if profile_user:
        user_posts = Post.objects.filter(user_id=profile_user).order_by('-post_timestamp')
        user_posts_and_likes = [(post, len(Like.objects.filter(post_id=post))) for post in user_posts]
        #profile_user_profile = Profile.objects.get(user_id=request.user.id)
        profile_user_profile = Profile.objects.get(user_id=user_id) #SRM
        
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


def get_user_profile_collections(request, user_id):
    try:
        profile_user = Auth_User.objects.get(pk=user_id)
    except Auth_User.DoesNotExist:
        profile_user = None
    if profile_user:
        profile_user_profile = Profile.objects.get(user_id=profile_user)
        profile_context = {'profile_user': profile_user,
                   'profile_user_profile': profile_user_profile}
        try:
            collections = Collection.objects.filter(user_id=profile_user)
            collections_and_posts = [ (collection, CollectionPost.objects.filter(collection_id=collection))\
                                for collection in collections ]
            profile_context['collections_and_posts'] = collections_and_posts
        except Collection.DoesNotExist:
            pass

    loggedin_user_context = twitter_user_context(request)

    context = {**profile_context, **loggedin_user_context}

    template = loader.get_template('rambleapp/user_collections.html')
    return HttpResponse(template.render(context, request))


def get_ramblepost(request, post_id):
    try:
        print("In ramble post")
        post = Post.objects.get(pk=post_id)
        post_likes = len(Like.objects.filter(post_id=post))
        comments = Comment.objects.filter(post_id=post, depth=0)
        commenters = [comment.user_id for comment in comments]
        commenter_profiles = {profile.user_id : profile 
                        for profile in Profile.objects.all().filter(user_id__in=commenters)}
        comment_and_profile_list = [(comment, commenter_profiles[comment.user_id]) for comment in comments]
        context = {'post': post, 'num_likes': post_likes, \
            'comments_and_profiles': comment_and_profile_list }

    except Post.DoesNotExist:
        post = None
        context = {}

    loggedin_user_context = twitter_user_context(request)

    total_context = {**context, **loggedin_user_context}

    template = loader.get_template('rambleapp/post.html')
    return HttpResponse(template.render(total_context, request))


def get_collection(request, collection_id):
    try:
        collection = Collection.objects.get(pk=collection_id)
        collection_posts = CollectionPost.objects.filter(collection_id=collection)
        collection_user_profile = Profile.objects.get(user_id=collection.user_id)
        context = {'collection': collection, 'collection_posts': collection_posts, 'collector_profile': collection_user_profile}
    except Collection.DoesNotExist:
        context = {}

    loggedin_user_context = twitter_user_context(request)

    total_context = {**context, **loggedin_user_context}

    template = loader.get_template('rambleapp/collection.html')
    return HttpResponse(template.render(total_context, request))


@login_required
def get_user_collections(request, post_id):
    try:
        user = Auth_User.objects.get(pk=request.user.id)
    except Auth_User.DoesNotExist:
        context = {}
    try:
        collections = Collection.objects.filter(user_id=user)
        relevant_collections = CollectionPost.objects.filter(post_id__pk=post_id, collection_id__user_id=user)
        context = {'collections': collections, 'post_id': post_id}
        if relevant_collections:
            context['relevant_collections'] = [coll.collection_id.pk for coll in relevant_collections]
            print(context['relevant_collections'])
    except Collection.DoesNotExist:     
        context = {}

    template = loader.get_template('rambleapp/collection_modal.html')
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
    if request.method == 'POST':
        user = Auth_User.objects.get(pk=request.user.id)
        form = ProfileForm(request.POST, request.FILES)
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
def post_comment(request):
    if request.method == 'POST':
        user = Auth_User.objects.get(pk=request.user.id)
        post_id = request.POST['post_id']
        post = Post.objects.get(pk=post_id)
        if not post:
            return HttpResponse(status=400)
        comment_text = request.POST['comment_text']
        depth = 0
        if 'parent_comment' in request.POST:
            parent_comment_id = request.POST['parent_comment']
        else:
            parent_comment_id = None
        if parent_comment_id: 
            parent_comment = Comment.objects.get(pk=parent_comment_id)
            depth = parent_comment.depth + 1
            if parent_comment.post_id != post: 
                return HttpResponse(status=400)
        else: 
            parent_comment = None 
        new_comment = Comment(user_id=user, post_id=post, comment_text=comment_text, 
                                parent_id=parent_comment, depth=depth)
        new_comment.save()
        #return HttpResponse(status=204)
        return HttpResponse(status=200) #SRM
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
def delete_comment(request):
    user = Auth_User.objects.get(pk=request.user.id)
    comment_id = request.POST['comment_id']
    comment = Comment.objects.get(pk=comment_id)
    if not comment:
        return HttpResponse(status=400)
    if comment.user_id == user:
        comment.delete()
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
    except Auth_User.DoesNotExist:
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


@login_required
def create_collection(request):
    if request.method == 'POST':
        user_id = request.user.id 
        try:
            collector = Auth_User.objects.get(pk=user_id)
        except Auth_User.DoesNotExist:
            return HttpResponse(status=400)
        collection_name = request.POST['collection_name']
        collection_desc = request.POST['collection_desc']

        new_collection = Collection(user_id=collector, \
            collection_name=collection_name, collection_desc=collection_desc)
        new_collection.save()
        col_dict = {}
        col_dict['id'] = new_collection.pk 
        col_dict['name'] = collection_name
        return HttpResponse(json.dumps(col_dict))


@login_required
def add_to_collection(request):
    if request.method == 'POST':
        user_id = request.user.id 
        try:
            collector = Auth_User.objects.get(pk=user_id)
        except Auth_User.DoesNotExist:
            return HttpResponse(status=400, reason="User does not exist!")
        collection_id = request.POST['collection_id']
        try:
            collection = Collection.objects.get(pk=collection_id)
        except Collection.DoesNotExist:
            return HttpResponse(status=400, reason="Collection does not exist!")
        post_id = request.POST['post_id']
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return HttpResponse(status=400, reason="Post does not exist!")
        if collector != collection.user_id:
            return HttpResponse(status=400, reason="user isn't owner of the collection!")
        print(request.POST)
        user_comment = request.POST['user_comments']
        print(collection, post, user_comment)
        new_collection_post = CollectionPost(collection_id=collection, post_id=post, user_comment=user_comment)
        new_collection_post.save()
        return HttpResponse(204)

    return HttpResponseForbidden('allowed only via POST')
