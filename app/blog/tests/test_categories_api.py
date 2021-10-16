from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Category, Post

from blog.serializers import CategorySerializer


CATEGORIES_URL = reverse('blog:category-list')


class PublicCategoriesApiTests(TestCase):
    """
    Test Categories API which requires no authentication
    """

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """
        Test that login is required to access this endpoint
        """
        res = self.client.get(CATEGORIES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateCategoriesAPITests(TestCase):
    """
    Test that categories can only be accessed by authorized user
    """

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@muteshi.co.ke',
            'testpass@125'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_category_list(self):
        """
        Test retrieving a list of categories
        """
        # categories list
        Category.objects.create(user=self.user, name='Technology')
        Category.objects.create(user=self.user, name='Politics')

        res = self.client.get(CATEGORIES_URL)

        categories = Category.objects.all().order_by('-name')
        serializer = CategorySerializer(categories, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_categories_limited_to_user(self):
        """
        Test that only categories for authenticated user are returned
        """
        user2 = get_user_model().objects.create_user(
            'otheruser@muteshi.co.ke',
            'testpass'
        )
        Category.objects.create(user=user2, name='Demo category')

        category = Category.objects.create(user=self.user, name='Testing')

        res = self.client.get(CATEGORIES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], category.name)

    def test_create_category_successful(self):
        """
        Test successful creation of a new category
        """
        payload = {'name': 'Resume'}
        self.client.post(CATEGORIES_URL, payload)

        category_exists = Category.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(category_exists)

    def test_create_category_invalid(self):
        """
        Test creating of category with invalid info fails
        """
        payload = {'name': ''}
        res = self.client.post(CATEGORIES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_cats_assigned_to_posts(self):
        """
        Test filtering categories by only those assigned to posts
        """
        cat1 = Category.objects.create(
            user=self.user, name='Cat1'
        )
        cat2 = Category.objects.create(
            user=self.user, name='cat2'
        )
        post = Post.objects.create(
            title='Psoting here',
            content='Heheheheh',
            author=self.user
        )
        post.category.add(cat1)

        res = self.client.get(CATEGORIES_URL, {'assigned_only': 1})

        serializer1 = CategorySerializer(cat1)
        serializer2 = CategorySerializer(cat2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_category_assigned_unique(self):
        """
        Test filtering category by assigned returns unique items
        """
        cat = Category.objects.create(user=self.user, name='cat1')
        Category.objects.create(user=self.user, name='cat2')
        post1 = Post.objects.create(
            title='Second Test',
            content='Content testing',
            author=self.user
        )
        post1.category.add(cat)
        post2 = Post.objects.create(
            title='Post theree testing',
            content='Content testing',
            author=self.user
        )
        post2.category.add(cat)

        res = self.client.get(CATEGORIES_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
