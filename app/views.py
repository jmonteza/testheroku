from django.shortcuts import render, redirect
from django.http import *
from .forms import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import *
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from django.contrib import messages
from django.core.serializers import *

from django.core import serializers
from django.http import JsonResponse

from django.contrib.auth.models import User
from .helpers import *
from django.db.models import Q


class HttpResponseUnauthorized(HttpResponse):
    status_code = 401

@require_http_methods(["GET"])
def root(request):
    # redirects to home page
    return redirect(reverse('home'))


@require_http_methods(["GET", "POST"])
def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            display_name = form.cleaned_data.get('display_name')
            try:
                first_name, last_name = display_name.split()
            except ValueError:
                first_name = display_name
                last_name = ""

            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            github = form.cleaned_data.get('github')
            password = form.cleaned_data.get('password')
            confirm_password = form.cleaned_data.get('confirm_password')

            if not is_valid_info(request, username, email, github, password, confirm_password):
                return redirect(reverse('signup'))

            try:
                u = User.objects.create_user(
                    username, email, password, first_name=first_name, last_name=last_name)
            except Exception as e:
                messages.warning(request, e)
                return redirect(reverse('signup'))
            else:
                u.save()

            try:
                Author.objects.create(host="http://127.0.0.1:8000", displayName=display_name,
                                      github=f"https://github.com/{github}", profileImage=None, email=email, username=username, confirmed=False)
            except Exception as e:
                messages.warning(request, e)
                return redirect(reverse('signup'))

            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect(reverse('home'))
                else:
                    messages.warning(
                        request, "Please contact the admin to get confirmed and be able to login")
                    return redirect(reverse('login'))
            else:
                messages.warning(request, "Please contact the admin to get confirmed and be able to login")
                return redirect(reverse('signup'))
        else:
            return redirect(reverse('signup'))

    elif request.method == "GET":
        if request.user.is_authenticated:
            return redirect(reverse('home'))
        else:
            context = {"title": "signup", "form": SignupForm()}
            return render(request, 'signup.html', context)


@require_http_methods(["GET"])
@login_required(login_url="/login")
def home(request): 
    user = request.user
    author = Author.objects.get(username=user.username)
    posts1 = Post.objects.filter(visibility="PUBLIC")
    posts2 = Post.objects.filter(visibility="FRIENDS", made_by__in=author.following.all())
    posts = (posts1 | posts2).order_by('-date_published')
    context = {"posts": posts, "comment_form": CommentForm()}
    return render(request, 'posts_stream.html', context)


@login_required(login_url="/login")
@require_http_methods(["GET", "POST"])
def author_search(request):

    if request.POST.get('action') == 'author-search':
        search_term = str(request.POST.get('query_term'))

        if search_term:
            search_term = Author.objects.filter(
                username__icontains=search_term)[:5]

            data = serializers.serialize('json', list(
                search_term), fields=('id', 'username'))

            return JsonResponse({'search_term': data})


def delete_post(request, post_id):
    post = Post.objects.get(uuid=post_id)

    if request.method == 'POST':
        # Verify that the user is allowed to delete the post
        if post.made_by.username != request.user.username:
            return JsonResponse({'success': False, 'message': 'You are not authorized to delete this post.'})

        # Delete the post
        post.delete()

        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


@login_required(login_url="/login")
@require_http_methods(["GET", "POST"])
def add_post(request):
    user = Author.objects.get(username=request.user.username)

    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            # Save the form data to the database
            if request.POST['visibility'] == 'PRIVATE':
                post = form.save(user=user, receiver_list = request.POST.getlist('receivers'))
                for reciever in post.recievers.all():
                    add_to_inbox(user,reciever,Activity.POST,post)
            else:
                 post = form.save(user=user)
                 for follower in user.followers.all():
                    add_to_inbox(user,follower,Activity.POST,post)
            # Do something with the saved data (e.g. redirect to a detail view)
            # return redirect('post_detail', pk=post.pk)

            return redirect(reverse('home'))
    elif request.method == "GET":
        context = {"title": "Create a Post", "form": PostForm()}
        return render(request, 'post.html', context)


@require_http_methods(["GET", "POST"])
def signin(request):
    if request.method == "POST":
        form = SigninForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
         
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect(reverse('home'))
                else:
                    messages.warning(request, "Your account is not confirmed. Please contact the admin to get their approval.")
                    return redirect(reverse('login'))
            else:
                messages.warning(request, "Invalid username, invalid password, or unconfirmed user.")
                return redirect(reverse('login'))
    elif request.method == "GET":
        # No need to sign in again
        if request.user.is_authenticated:
            return redirect(reverse('home'))
        else:
            context = {"title": "signin", "form": SigninForm()}
            return render(request, 'signin.html', context)


@login_required(login_url="/login")
@require_http_methods(["GET", "POST"])
def signout(request):
    if request.method == "GET":
        logout(request)
        return redirect(reverse('home'))


@login_required(login_url="/login")
@require_http_methods(["GET", "POST"])
def authors(request):
    if request.method == "GET":
        authors = list(Author.objects.exclude(Q(
            username=request.user.username) | Q(confirmed=False)).order_by('displayName'))
        current_user_followings = Author.objects.get(
            username=request.user.username).following.all()
        current_user_sent_requests = Author.objects.get(
            username=request.user.username).sent_requests.all()

        ineligible_users = current_user_followings | current_user_sent_requests

        context = {"authors": authors, "ineligible_users": ineligible_users}
        return render(request, 'authors.html', context)

    elif request.method == "POST":
        # Get the username to follow
        id_to_follow = request.POST.get("follow")

        # Get the author object
        author_to_follow = Author.objects.get(id=id_to_follow)

        # Get our author object
        current_user_author = Author.objects.get(
            username=request.user.username)

        # Add the author object to our sent_request list (Need to send this to inbox in the future to get approval on the other end)
        current_user_author.sent_requests.add(author_to_follow)
        add_to_inbox(current_user_author,author_to_follow,Activity.FOLLOW,current_user_author)

        return redirect(reverse("authors"))


@login_required(login_url="/login")
@require_http_methods(["GET", "POST"])
def profile(request, author_id):
    user = request.user
    userAuthor = Author.objects.get(username=request.user.username)
    if request.method == 'GET':
        author = Author.objects.get(id=author_id)
        username = author.username
        following = author.following.all().order_by('displayName')
        followers = author.followers.all().order_by('displayName')
        friends = list(following & followers)
        posts = get_posts_visible_to_user(userAuthor, author, friends)
        context = {"posts": posts, "comment_form": CommentForm()}
        context.update({"author": author, "following": following, "followers": followers, "friends": friends, "user": user, "active_tab": "posts"})
        try:
            userFollows = userAuthor.following.get(username=username)
            context.update({"user_is_following": "True"})
        except:
            context.update({"user_is_following": "False"})

        return render(request, 'profile.html', context)
    
    elif request.method == "POST":
        author_for_action = Author.objects.get(id=author_id)
        if author_for_action in userAuthor.following.all():
            # Remove the author from the following of the current user
            userAuthor.following.remove(author_for_action)
        else:
            # Add the author object to our sent_request list (Need to send this to inbox in the future to get approval on the other end)
            userAuthor.sent_requests.add(author_for_action)

        return redirect(reverse("profile", kwargs={"author_id": userAuthor.id}))
    

def get_posts_visible_to_user(userAuthor, author, friends):
    if userAuthor.id==author.id:
        return Post.objects.filter(made_by=author).order_by('-date_published')
    public = Post.objects.filter(made_by=author, visibility="PUBLIC")
    #private = Post.objects.filter(made_by=author, receivers__contains=user)
    if userAuthor in friends:
        friends = Post.objects.filter(made_by=author, visibility="FRIENDS")
        #posts = (private | public | friends).distinct()
        posts = (public | friends).distinct()
    else:
        #posts = (private | public).distinct()
        posts = public

    return posts.order_by('-date_published')

@login_required(login_url="/login")
@require_http_methods(["POST"])
def unfollow(request):
    user = request.user
    # Extract the username of the author to unfollow
    id_to_unfollow = request.POST.get("unfollow")
    # Get the author object to unfollow
    author_to_unfollow = Author.objects.get(id=id_to_unfollow)
    # Get the author object of the current user
    user_author = Author.objects.get(username=user)
    # Remove the author from the following of the current user
    user_author.following.remove(author_to_unfollow)
    
    return redirect(reverse("profile", kwargs={"author_id": user_author.id}))

@login_required(login_url="/login")
@require_http_methods(["POST"])
def removeFollower(request):
    user = request.user
    # Extract the username of the author to remove from our followers
    id_to_remove = request.POST.get("removefollower")
    # Get the author object
    author_to_remove = Author.objects.get(id=id_to_remove)
    # Get our author object
    user_author = Author.objects.get(username=user.username)
    # We remove ourself to the author's followings list
    author_to_remove.following.remove(user_author)

    return redirect(reverse("profile", kwargs={"author_id": user_author.id}))

@login_required(login_url="/login")
@require_http_methods(["GET"])
def true_friends(request, username):
    if request.method == 'GET':

        author = Author.objects.get(username=username)

        followings = set(author.following.all())

        followers = set(author.followers.all())

        true_friends = list(followings & followers)

        context = {"friends": true_friends, "author": author}

        return render(request, 'true-friends.html', context)


@login_required(login_url="/login")
@require_http_methods(["GET", "POST"])
def received_requests(request, author_id):
    user = request.user

    if request.method == 'GET':

        follow_requests = Author.objects.get(
            username=request.user.username).follow_requests.all()

        context = {"requests": follow_requests, "mode": "received"}

        return render(request, 'requests.html', context)

    elif request.method == "POST":
        response = ""
        inbox = None
        request_action = request.POST.get("action").split("_")
        if len(request_action) < 2:
            return HttpResponseBadRequest("Not enough action parameters")
        action = request_action[0]
        sender_username = request_action[1]
        if len(request_action) > 2:
            inbox = request_action[2]
        sender_author = Author.objects.get(username=sender_username)

        # Get our author object
        current_user_author = Author.objects.get(
            username=request.user.username)

        if action == "accept":
            # Add ourself to the sender author's following
            sender_author.following.add(current_user_author)

            # Remove this follow request on the sender side
            sender_author.sent_requests.remove(current_user_author)

            # Remove this follow request on our side
            current_user_author.follow_requests.remove(sender_author)
            response = "Accepted"

        elif action == "decline":

            # Remove this follow request on the sender side
            sender_author.sent_requests.remove(current_user_author)

            # Remove this follow request on our side
            current_user_author.follow_requests.remove(sender_author)
            response = "Declined"

        if inbox:
            return redirect(reverse("inbox", kwargs={'author_id': convert_username_to_id(user.username)}))
        return redirect(reverse("requests", kwargs={'author_id': convert_username_to_id(user.username)}))


@login_required(login_url="/login")
@require_http_methods(["GET", "POST"])
def sent_requests(request, author_id):
    user = request.user

    if request.method == 'GET':

        sent_requests = Author.objects.get(
            username=request.user.username).sent_requests.all()

        context = {"requests": sent_requests, "mode": "sent"}

        return render(request, 'requests.html', context)

    elif request.method == "POST":
        action, receiver_username = request.POST.get("action").split("_")

        receiver_author = Author.objects.get(username=receiver_username)

        # Get our author object
        current_user_author = Author.objects.get(
            username=request.user.username)

        if action == "cancel":
            # Remove it from our sent requests
            current_user_author.sent_requests.remove(receiver_author)

            # Remove it from the receiver side
            receiver_author.follow_requests.remove(current_user_author)

        return redirect(reverse("sent_requests", kwargs={'author_id': convert_username_to_id(user.username)}))


@login_required(login_url="/login")
@require_http_methods(["GET"])
def posts(request):
    posts = Post.objects.all().order_by('-date_published')

    context = {"posts": posts, "comment_form": CommentForm()}

    return render(request, 'posts_stream.html', context)


@login_required(login_url="/login")
@require_http_methods(["GET"])
def post_detail(request, post_id):
    post = Post.objects.get(uuid=post_id)
    context = {"request": request, "post": post, "comment_form": CommentForm()}

    return render(request, 'post_detail.html', context)


@login_required(login_url="/login")
@require_http_methods(["GET","POST"])
def inbox(request, author_id):

    # Requested author
    requested_author = Author.objects.get(id=author_id)

    # Current user's author
    author = Author.objects.get(username=request.user.username)

    if requested_author.username != author.username:
        return HttpResponseUnauthorized()
    context = {"type": "inbox"}

    if request.method == "GET":
        all = author.my_inbox.all().order_by("-date")
        likes = all.filter(object__type="like")
        comments = all.filter(object__type="comment")
        posts = all.filter(object__type="post")
        requests = all.filter(object__type="follow")
        context.update({"items": all, "likes": likes, "comments": comments, "posts": posts, "requests": requests})

    elif request.method == "POST" and request.POST.get("action")=="clear_inbox":
        author.my_inbox.all().delete()

    return render(request, 'inbox.html', context)

@login_required(login_url="/login")
@require_http_methods(["POST"])
def add_comment(request,post_id):
    user = Author.objects.get(username=request.user.username)
    post = Post.objects.get(uuid=post_id)

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(user=user,post=post)
            add_to_inbox(user,post.made_by,Activity.COMMENT,post)

            # Do something with the saved data (e.g. redirect to a detail view)
            # return redirect('post_detail', pk=post.pk)

            return redirect(reverse('post_detail',kwargs={'post_id': post.uuid}))

@login_required(login_url="/login")
@require_http_methods(["POST"])
def add_like_post(request,post_id):
    user = Author.objects.get(username=request.user.username)
    post = Post.objects.get(uuid=post_id)
    response = HttpResponse()

    if request.method == "POST":
        if post.made_by.username == user.username:
            response.content = "Can't like your own post."
            return response
        found = post.likes.filter(author=user)
        if not found:
            post.likes.create(type=Like.POST,author=user,summary=f'{user.displayName} liked your post.')
            add_to_inbox(user,post.made_by,Activity.LIKE,post)
            response.content = "Liked"
        else:
            response.content = "Already liked this post."

    return response

@login_required(login_url="/login")
@require_http_methods(["POST"])
def add_like_comment(request,post_id,comment_id):
    user = Author.objects.get(username=request.user.username)
    post = Post.objects.get(uuid=post_id)
    comment = Comment.objects.get(uuid=comment_id)
    response = HttpResponse()

    if request.method == "POST":
        if comment.author.username == user.username:
            response.content = "Can't like your own comment."
            return response
        found = comment.likes.filter(author=user)
        if not found:
            comment.likes.create(type=Like.COMMENT,author=user,summary=f'{user.displayName} liked your comment.')
            add_to_inbox(user,comment.author,Activity.LIKE,comment)
            response.content = "Liked"
        else:
            response.content = "Already liked this comment."

    return response
