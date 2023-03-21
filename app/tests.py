from django.test import TestCase

from .models import Author

from django.core.exceptions import ValidationError, ObjectDoesNotExist

class AuthorTest(TestCase):

    host = 'http://127.0.0.1:8000'

    displayName = 'John Doe'

    github = 'https://github.com/johndoe'

    profileImage = 'https://images.pexels.com/photos/220453/pexels-photo-220453.jpeg'

    email = 'johndoe@gmail.com'

    username = 'johndoe'

    confirmed = True

    def create_author(self):
        author = Author(host=self.host, displayName=self.displayName,
                        github=self.github, profileImage=self.profileImage, email=self.email, username=self.username, confirmed=self.confirmed)

        author.full_clean()
        author.save()
        return author
    
    def test_create_author(self):
        author = self.create_author()
        self.assertTrue(isinstance(author, Author))
        # self.assertEqual(str(user), f"{self.name} ({self.email})")

    def test_create_author_empty(self):

        # Empty Argument
        author = Author()
        self.assertRaises(ValidationError, author.full_clean)

        # Empty host
        author = Author(host=None, displayName=self.displayName,
               github=self.github, profileImage=self.profileImage, email=self.email, username=self.username, confirmed=self.confirmed)
        self.assertRaises(ValidationError, author.full_clean)

        # Empty display name
        author = Author(host=self.host, displayName=None,
               github=self.github, profileImage=self.profileImage, email=self.email, username=self.username, confirmed=self.confirmed)
        self.assertRaises(ValidationError, author.full_clean)

        # Empty github
        author = Author(host=self.host, displayName=self.displayName,
                        github=None, profileImage=self.profileImage, email=self.email, username=self.username, confirmed=self.confirmed)
        self.assertRaises(ValidationError, author.full_clean)

        # Empty profileImage
        author = Author(host=self.host, displayName=self.displayName,
                        github=self.github, profileImage=None, email=self.email, username=self.username, confirmed=self.confirmed)
        self.assertRaises(ValidationError, author.full_clean)

        # Empty email
        author = Author(host=self.host, displayName=self.displayName,
                        github=self.github, profileImage=self.profileImage, email=None, username=self.username, confirmed=self.confirmed)
        self.assertRaises(ValidationError, author.full_clean)

        # Empty username
        author = Author(host=self.host, displayName=self.displayName,
                        github=self.github, profileImage=self.profileImage, email=self.email, username=None, confirmed=self.confirmed)
        self.assertRaises(ValidationError, author.full_clean)

    def test_create_author_invalid_argument(self):

        # Invalid host URL
        author = Author(host=123, displayName=self.displayName,
                        github=self.github, profileImage=self.profileImage, email=self.email, username=self.username, confirmed=self.confirmed)
        self.assertRaises(ValidationError, author.full_clean)

        # Invalid github URL
        author = Author(host=self.host, displayName=self.displayName,
                        github=456, profileImage=self.profileImage, email=self.email, username=self.username, confirmed=self.confirmed)
        self.assertRaises(ValidationError, author.full_clean)

        # Invalid profileImage URL
        author = Author(host=self.host, displayName=self.displayName,
                        github=self.github, profileImage=789, email=self.email, username=self.username, confirmed=self.confirmed)
        self.assertRaises(ValidationError, author.full_clean)

        # Invalid email
        author = Author(host=self.host, displayName=self.displayName,
                        github=self.github, profileImage=self.profileImage, email='google.com', username=self.username, confirmed=self.confirmed)
        self.assertRaises(ValidationError, author.full_clean)


    def test_add_author_to_db(self):
        author = Author(host=self.host, displayName="Jane Doe",
                        github=self.github, profileImage=self.profileImage, email=self.email, username=self.username, confirmed=self.confirmed)

        author.full_clean()
        author.save()

        retrieved_author = Author.objects.get(displayName="Jane Doe")

        self.assertEqual(retrieved_author.displayName, "Jane Doe")

    def test_delete_author_from_db(self):
        author = Author(host=self.host, displayName="Deleted Author",
                        github=self.github, profileImage=self.profileImage, email=self.email, username=self.username, confirmed=self.confirmed)
        
        author.full_clean()
        author.save()

        retrieved_author = Author.objects.get(displayName="Deleted Author")

        self.assertEqual(retrieved_author.displayName, "Deleted Author")
        
        retrieved_author.delete()

        # Reference: https: // stackoverflow.com/questions/69781507/django-unit-test-an-object-has-been-deleted-how-to-use-assertraise-doesnot
        with self.assertRaises(Author.DoesNotExist):
            Author.objects.get(displayName="Deleted Author")

    def test_update_author_in_db(self):
        author = Author(host=self.host, displayName="Jamie Doe",
                        github=self.github, profileImage=self.profileImage, email=self.email, username=self.username, confirmed=self.confirmed)

        author.full_clean()
        author.save()

        retrieved_author = Author.objects.get(displayName="Jamie Doe")

        self.assertEqual(retrieved_author.displayName, "Jamie Doe")

        retrieved_author.displayName = "Anna Doe"

        retrieved_author.save()

        retrieved_author = Author.objects.get(displayName="Anna Doe")

        self.assertEqual(retrieved_author.displayName, "Anna Doe")



  
