from django.urls import reverse, resolve
from urllib.parse import urlparse

def get_full_uri(request,view_name,kwargs={},remove_str='api/') -> str:
  return str(request.build_absolute_uri(reverse(view_name, kwargs=kwargs))).replace(remove_str,'')

def get_values_from_uri(path,add_api=False):
  if add_api:
    parsed_uri = urlparse(path)
    path = f'/api{parsed_uri.path}'
  func, args, kwargs = resolve(path)
  return kwargs
