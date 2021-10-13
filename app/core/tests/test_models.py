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