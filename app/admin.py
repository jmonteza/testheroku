from django.contrib import admin

from .models import *

# Register your models here.
admin.site.register([
  Author,
  Post,
  Comment,
  Like,
  Inbox,
  Activity,
  Node,
  ])


