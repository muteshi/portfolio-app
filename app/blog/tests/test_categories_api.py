from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Category

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

    # def test_create_ingredient_successful(self):
    #     """
    #     Test successful creation of a new ingredient
    #     """
    #     payload = {'name': 'Cabbage'}
    #     self.client.post(INGREDIENTS_URL, payload)

    #     ing_exists = Ingredient.objects.filter(
    #         user=self.user,
    #         name=payload['name']
    #     ).exists()
    #     self.assertTrue(ing_exists)

    # def test_create_ingredient_invalid(self):
    #     """
    #     Test creating of ingredient with invalid info fails
    #     """
    #     payload = {'name': ''}
    #     res = self.client.post(INGREDIENTS_URL, payload)

    #     self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_retrieve_ingredients_assigned_to_recipes(self):
    #     """
    #     Test filtering ingredients by only those assigned to recipes
    #     """
    #     ingredient1 = Ingredient.objects.create(
    #         user=self.user, name='Apples'
    #     )
    #     ingredient2 = Ingredient.objects.create(
    #         user=self.user, name='Turkey'
    #     )
    #     recipe = Recipe.objects.create(
    #         title='Apple crumble',
    #         duration=5,
    #         price=10.00,
    #         user=self.user
    #     )
    #     recipe.ingredients.add(ingredient1)

    #     res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

    #     serializer1 = IngredientSerializer(ingredient1)
    #     serializer2 = IngredientSerializer(ingredient2)
    #     self.assertIn(serializer1.data, res.data)
    #     self.assertNotIn(serializer2.data, res.data)

    # def test_retrieve_ingredient_assigned_unique(self):
    #     """
    #     Test filtering ingredients by assigned returns unique items
    #     """
    #     ingredient = Ingredient.objects.create(user=self.user, name='Eggs')
    #     Ingredient.objects.create(user=self.user, name='Cheese')
    #     recipe1 = Recipe.objects.create(
    #         title='Eggs benedict',
    #         duration=30,
    #         price=12.00,
    #         user=self.user
    #     )
    #     recipe1.ingredients.add(ingredient)
    #     recipe2 = Recipe.objects.create(
    #         title='Green eggs on toast',
    #         duration=20,
    #         price=5.00,
    #         user=self.user
    #     )
    #     recipe2.ingredients.add(ingredient)

    #     res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

    #     self.assertEqual(len(res.data), 1)