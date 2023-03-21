from django.contrib.auth.models import User
from .models import *
from django.contrib import messages


def username_exists(username):
    return User.objects.filter(username=username).exists()


def email_address_exists(email):
    return User.objects.filter(email=email).exists()


def github_exists(github):
    return Author.objects.filter(github=f"https://github.com/{github}").exists()


def is_valid_info(request, username, email, github, password, confirm_password):
    if username_exists(username):
        messages.warning(request, "Username is not available.")
        return False

    elif email_address_exists(email):
        messages.warning(request, "Email address is already in use.")
        return False

    elif github_exists(github):
        messages.warning(request, "Github username is already in use.")
        return False

    elif password != confirm_password:
        messages.warning(request, "Passwords do not match.")
        return False

    else:
        return True


def add_to_inbox(from_author,to,type,object):
    if from_author != to:
        activity = Activity.objects.create(type=type,content_object=object)
        return Inbox.objects.create(from_author=from_author,to=to,object=activity)
    return None

def convert_username_to_id(username):
    return Author.objects.get(username=username).id
