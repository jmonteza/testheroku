from django.urls import path

from . import views
from .API.views import *

from django.urls import include, re_path
from rest_framework_swagger.views import get_swagger_view

from rest_framework.schemas import get_schema_view

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="Social Distribution API Documentation",
        default_version='v1',
        description="CMPUT 404",
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


urlpatterns = [

    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger',
            cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc',
                                             cache_timeout=0), name='schema-redoc'),
    path('', views.root, name='root'),    
    path('signup', views.signup, name='signup'),
    path('home', views.home, name='home'),
    path('post', views.add_post, name='post-form'),
    path('author/search', views.author_search, name='author-search'),
    path('login', views.signin, name='login'),
    path('logout', views.signout, name='logout'),
    path('posts', views.posts, name='posts'),
    path('posts/<str:post_id>', views.post_detail, name='post_detail'),
    path('posts/<str:post_id>/comment', views.add_comment, name='comment-form'),
    path('posts/<str:post_id>/like', views.add_like_post, name='add_like_post'),
    path('posts/<str:post_id>/comments/<str:comment_id>/like', views.add_like_comment, name='add_like_comment'),
    path('delete-post/<uuid:post_id>/', views.delete_post, name='delete_post'),

    path('authors', views.authors, name='authors'),
    path('authors/<uuid:author_id>/inbox', views.inbox, name='inbox'),
    path('authors/<str:author_id>', views.profile, name='profile'),
    path('unfollow', views.unfollow, name='unfollow'),
    path('removefollower', views.removeFollower, name='removefollower'),
    path('authors/<uuid:author_id>', views.profile, name='profile'),
    path('<str:username>/true-friends', views.true_friends, name='true-friends'),
    path('authors/<uuid:author_id>/received', views.received_requests, name='requests'),
    path('authors/<uuid:author_id>/sent', views.sent_requests, name='sent_requests'),

    #API urls
    path('api/authors', AuthorListAPIView.as_view(), name='api-author-list'),
    path('api/authors/<uuid:author_id>', SingleAuthorAPIView.as_view(), name='api-single_author'),
    path('api/authors/<uuid:author_id>/followers', AuthorFollowersAPIView.as_view(), name='api-author-followers'),
    path('api/authors/<uuid:author_id>/followers/<uuid:follower_author_id>', FollowerAPIView.as_view(), name='api-followers'),
    path('api/authors/<uuid:author_id>/posts/<uuid:post_id>', PostDetailView.as_view(), name ='api-post-detail'),
    path('api/authors/<uuid:author_id>/posts', AuthorPostsView.as_view(), name ='api-author-post'),
    path('api/authors/<uuid:author_id>/liked', LikedView.as_view(), name ='api-author-liked'),
    path('api/authors/<uuid:author_id>/inbox', InboxView.as_view(), name ='api-author-inbox'),
    path('api/authors/<uuid:author_id>/posts/<uuid:post_id>/comments', CommentsView.as_view(), name ='api-post-comments'),
    path('api/authors/<uuid:author_id>/posts/<uuid:post_id>/likes', LikesPostView.as_view(), name ='api-post-likes'),
    path('api/authors/<uuid:author_id>/posts/<uuid:post_id>/comments/<uuid:comment_id>', CommentView.as_view(), name ='api-post-comment'),
    path('api/authors/<uuid:author_id>/posts/<uuid:post_id>/comments/<uuid:comment_id>/likes', LikesCommentView.as_view(), name ='api-post-comment-likes'),

]
