from rest_framework.test import APITestCase,APIRequestFactory
from rest_framework import status
from .views import *
from django.urls import reverse
from ..models import *
from django.contrib.auth import get_user_model

User = get_user_model()

def create_authors(length):
  user_list = []
  for i in range(length):
    user_list.append({'username': f'test{i+1}','email': f'test{i+1}@test.ca','password': 'test'})

  return setup_authors(user_list)

def setup_authors(authors):
  for user in authors:
    User.objects.create(
      username=user.get('username'),
      email=user.get('email'),
      password=user.get('password')
    )
    Author.objects.create(
      host="http://127.0.0.1:8000",
      displayName=user.get('username'),
      github=f"https://github.com/{user.get('username')}",
      profileImage=None, email=user.get('email'),
      username=user.get('username'),
      confirmed=True
    )
  return Author.objects.all()

# Create your tests here.
class Authors(APITestCase):

  def setUp(self):
    self.user =  User.objects.create(
        username='user',
        email='user@user.ca',
        password='user'
      )
    self.author_list = create_authors(5)


  def testAuthorList(self):
    kwargs = {

    }
    response = self.client.get(reverse('api-author-list',kwargs=kwargs))
    self.assertEquals(len(response.data.get('items')),len(self.author_list))

  def testAuthorSingle(self):
    author = self.author_list.first()
    kwargs = {
      'author_id': author.id,
    }
    response = self.client.get(reverse('api-single_author',kwargs=kwargs))
    self.assertEquals(response.data.get('displayName'),author.displayName)

  def testAuthorFollowers(self):
    author = self.author_list.first()
    author_follow = self.author_list.last()
    author_follow.following.add(author)
    kwargs = {
      'author_id': author.id,
    }
    response = self.client.get(reverse('api-author-followers',kwargs=kwargs))
    self.assertEquals(len(response.data.get('items')),len(author.followers.all()))
    self.assertEquals(response.data.get('items')[0].get('displayName'),author_follow.displayName)

  def testAuthorFollow(self):
    author = self.author_list.first()
    author_follow = self.author_list.last()
    author_follow.following.add(author)
    kwargs = {
      'author_id': author.id,
      'follower_author_id': author_follow.id
    }
    response = self.client.get(reverse('api-followers',kwargs=kwargs))
    self.assertEquals(response.data.get('is_following'),True)

  def testAuthorDeleteFollow(self):
    author = self.author_list.first()
    author_follow = self.author_list.last()
    author_follow.following.add(author)
    kwargs = {
      'author_id': author.id,
      'follower_author_id': author_follow.id
    }
    response = self.client.delete(reverse('api-followers',kwargs=kwargs))
    self.assertEquals(response.status_code,status.HTTP_204_NO_CONTENT)

    response = self.client.delete(reverse('api-followers',kwargs=kwargs))
    self.assertEquals(response.status_code,status.HTTP_404_NOT_FOUND)

  def testAuthorNotFollow(self):
    author = self.author_list.first()
    author_follow = self.author_list.last()
    kwargs = {
      'author_id': author.id,
      'follower_author_id': author_follow.id
    }
    response = self.client.get(reverse('api-followers',kwargs=kwargs))
    self.assertEquals(response.data.get('is_following'),False)


class Posts(APITestCase):

  def setUp(self):
    self.user =  User.objects.create(
        username='user',
        email='user@user.ca',
        password='user'
      )
    self.author_list = create_authors(5)

  def testGetAuthorPosts(self):
    author = self.author_list.first()
    author.my_posts.create(title="Test")
    author.my_posts.create(title="Test 2")
    author.my_posts.create(title="Test 3")
    kwargs = {
      'author_id': author.id,
    }
    response = self.client.get(reverse('api-author-post',kwargs=kwargs))

    self.assertEquals(len(response.data),len(author.my_posts.all()))

  def testGetAuthorPostPublic(self):
    author = self.author_list.first()
    post = author.my_posts.create(title="Test",visibility="PUBLIC")
    kwargs = {
      'author_id': author.id,
      'post_id': post.uuid
    }
    response = self.client.get(reverse('api-post-detail',kwargs=kwargs))

    self.assertEquals(response.data.get('title'),post.title)


  def testGetAuthorPostDelete(self):
    author = self.author_list.first()
    post = author.my_posts.create(title="Test",visibility="PUBLIC")
    kwargs = {
      'author_id': author.id,
      'post_id': post.uuid
    }
    response = self.client.delete(reverse('api-post-detail',kwargs=kwargs))
    self.assertEquals(response.status_code,status.HTTP_204_NO_CONTENT)

    response = self.client.delete(reverse('api-post-detail',kwargs=kwargs))
    self.assertEquals(response.status_code,status.HTTP_404_NOT_FOUND)

class Comments(APITestCase):

  def setUp(self):
    self.user =  User.objects.create(
        username='user',
        email='user@user.ca',
        password='user'
      )
    self.author_list = create_authors(5)
    self.post_author = self.author_list.first()
    self.post = self.post_author.my_posts.create(title="Test",visibility="PUBLIC")

  def testGetPostComment(self):
    author = self.author_list.last()
    comment = self.post.comments.create(author=author,comment="New comment")
    kwargs = {
      'author_id': self.post_author.id,
      'post_id': self.post.uuid,
      'comment_id': comment.uuid
    }
    response = self.client.get(reverse('api-post-comment',kwargs=kwargs))
    self.assertEquals(response.data.get('comment'),"New comment")

  def testGetPostComments(self):
    author = self.author_list.last()
    self.post.comments.create(author=author,comment="New comment")
    self.post.comments.create(author=author,comment="New comment2")
    kwargs = {
      'author_id': self.post_author.id,
      'post_id': self.post.uuid
    }
    response = self.client.get(reverse('api-post-comments',kwargs=kwargs))
    self.assertEquals(len(response.data.get('comments')),len(self.post.comments.all()))


class Likes(APITestCase):

  def setUp(self):
    self.user =  User.objects.create(
        username='user',
        email='user@user.ca',
        password='user',
      )
    self.author_list = create_authors(5)
    self.post_author = self.author_list.first()
    self.comment_author = self.author_list.last()
    self.post = self.post_author.my_posts.create(title="Test",visibility="PUBLIC")
    self.comment = self.post.comments.create(author=self.comment_author,comment='comment')

  def testGetPostLikes(self):
    self.post.likes.create(author=self.comment_author,summary="liked post")
    kwargs = {
      'author_id': self.post_author.id,
      'post_id': self.post.uuid
    }
    response = self.client.get(reverse('api-post-likes',kwargs=kwargs))
    self.assertEquals(response.data[0].get('summary'),"liked post")

    self.post.likes.create(author=self.comment_author,summary="liked post")
    response = self.client.get(reverse('api-post-likes',kwargs=kwargs))
    self.assertEquals(len(response.data),2)

  def testGetCommentLikes(self):
    self.post.likes.create(author=self.comment_author,summary="liked comment")
    self.comment.likes.create(author=self.post_author,summary="liked comment")
    kwargs = {
      'author_id': self.post_author.id,
      'post_id': self.post.uuid,
      'comment_id': self.comment.uuid
    }
    response = self.client.get(reverse('api-post-comment-likes',kwargs=kwargs))
    self.assertEquals(response.data[0].get('summary'),"liked comment")

    self.comment.likes.create(author=self.comment_author,summary="liked comment")
    response = self.client.get(reverse('api-post-comment-likes',kwargs=kwargs))
    self.assertEquals(len(response.data),2)

  def testGetAuthorLiked(self):
    self.post.likes.create(author=self.comment_author,summary="liked comment")
    self.comment.likes.create(author=self.post_author,summary="liked comment")
    self.comment.likes.create(author=self.post_author,summary="liked comment 2")
    kwargs = {
      'author_id': self.post_author.id,
    }
    response = self.client.get(reverse('api-author-liked',kwargs=kwargs))
    self.assertEquals(len(response.data),2)

class Inbox(APITestCase):

  def setUp(self):
    self.user =  User.objects.create(
        username='user',
        email='user@user.ca',
        password='user'
      )
    self.author_list = create_authors(5)

