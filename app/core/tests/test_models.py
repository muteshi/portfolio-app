from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models

email = 'test@muteshi.co.ke'
password = 'passYangu'


def test_user(email=email, password=password):
    """
    Function for creating sample test user
    """
    return get_user_model().objects.create_user(
        email,
        password,
    )


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = 'test@muteshi.com'
        password = 'Password123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        email = 'test@muTESHi.com'
        user = get_user_model().objects.create_user(email, 'test123')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_new_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            'test@muteshi.com',
            'test123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """
        Test the string representation of a tag model
        """
        tag = models.Tag.objects.create(
            user=test_user(),
            name='technology'
        )

        self.assertEqual(str(tag), tag.name)

    def test_category_str(self):
        """
        Test the string representation of a category model
        """
        category = models.Category.objects.create(
            user=test_user(),
            name='Hyper-V'
        )

        self.assertEqual(str(category), category.name)

    def test_post_str(self):
        """
        Test the string representation of the post model
        """
        post = models.Post.objects.create(
            author=test_user(),
            title='This is a test title',
            content='Hahaha this is it',
        )

        self.assertEqual(str(post), post.title)

    def test_skills_str(self):
        """
        Test the string representation of the Skills model
        """
        skill = models.Skill.objects.create(
            user=test_user(),
            title='Backend Development',
            percentage=7,
        )

        self.assertEqual(str(skill), skill.title)

    def test_photos_str(self):
        """
        Test the string representation of Photos model
        """
        photos = models.Photos.objects.create(
            user=test_user(),
            caption='test photo',
            title='testing photo'

        )
        self.assertEqual(str(photos), photos.title)

    def test_message_str(self):
        """
        Test the string representation of the Contact model
        """
        contact = models.Message.objects.create(
            name='Test Name',
            email='lumteshi@gmail.com',
            subject='Checking on you',
            comment='Here is my message',
        )

        self.assertEqual(str(contact), contact.name)

    @patch('uuid.uuid4')
    def test_post_file_name_uuid(self, mock_uuid):
        """
        Test that the uploaded image is saved in the correct location
        """
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.post_image_file_path(None, 'myimage.jpg')

        expected_path = f'uploads/post/{uuid}.jpg'
        self.assertEqual(file_path, expected_path)

    def test_post_slug_unique(self):
        """
        Test that the slug of posts are unique
        """
        user = test_user()
        post1 = models.Post.objects.create(
            author=user, title='Testing title', content='Testing content')
        post2 = models.Post.objects.create(
            author=user, title='Testing title', content='Testing content')

        self.assertNotEqual(post1.slug, post2.slug)
