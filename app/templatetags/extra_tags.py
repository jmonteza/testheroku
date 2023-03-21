# https://docs.djangoproject.com/en/4.1/howto/custom-template-tags/
from django import template
from ..models import *

register = template.Library()

@register.filter(name='classname')
def classname(obj):
  return obj.__class__.__name__

@register.filter(name='isRequest')
def is_request(user_id,id):
  user = Author.objects.get(id=id)
  return len(user.sent_requests.filter(id=user_id)) >= 1

@register.filter(name='isFollowing')
def is_following(user_id,id):
  user = Author.objects.get(id=id)
  return len(user.following.filter(id=user_id)) >= 1

@register.filter
def convert_username_to_id(value):
    return Author.objects.get(username=value).id

