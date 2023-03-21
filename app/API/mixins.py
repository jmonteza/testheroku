from django.contrib.auth.hashers import check_password
from django.http import HttpResponse
import base64
from ..models import Node


class BasicAuthMixin:
    def dispatch(self, request, *args, **kwargs):
        auth_header = request.META.get('HTTP_AUTHORIZATION')

        if not auth_header:
            response = HttpResponse('Authentication Required', status=401)
            response['WWW-Authenticate'] = 'Basic realm="API"'
            return response

        auth_type, auth_value = auth_header.split(' ', 1)

        if auth_type.lower() != 'basic':
            response = HttpResponse('Authentication Required', status=401)
            response['WWW-Authenticate'] = 'Basic realm="API"'
            return response

        username_password = base64.b64decode(auth_value.encode('utf-8')).decode('utf-8').split(':')
       
        username = username_password[0]
        password = username_password[1]

        if not self.authenticate(username, password):
            response = HttpResponse('Invalid username or password', status=401)
            response['WWW-Authenticate'] = 'Basic realm="API"'
            return response

    
        return super().dispatch(request, *args, **kwargs)

    def authenticate(self, username, password):
        try:

            client = Node.objects.get(username=username, password=password)
            return client
        except Node.DoesNotExist:
            return None