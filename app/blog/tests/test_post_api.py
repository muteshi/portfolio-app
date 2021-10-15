# import tempfile
import os

# from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
# from rest_framework import serializers
from rest_framework.test import APIClient

from core.models import Post, Tag, Category

from blog.serializers import PostSerializer, PostDetailSerializer


POSTS_URL = reverse('blog:post-list')


# def image_upload_url(recipe_id):
#     """
#     Return recipe's photo url
#     """
#     return reverse('recipe:recipe-upload-image', args=[recipe_id])


def detail_post_url(post_slug):
    """
    Return post details url
    """
    return reverse('blog:post-detail', args=[post_slug])


def test_tag(user, name='Test Tag'):
    """
    Create and return a sample test tag
    """
    return Tag.objects.create(user=user, name=name)


def test_category(user, name='Testing category'):
    """
    Create and return a sample test category
    """
    return Category.objects.create(user=user, name=name)


def test_post(user, **params):
    """
    Create and return a sample test post
    """
    defaults = {
        'title': 'testing post',
        'content': 'testing content',
    }
    defaults.update(params)

    return Post.objects.create(author=user, **defaults)


class PublicPostApiTests(TestCase):
    """
    Test public access of post API
    """

    def setUp(self):
        self.client = APIClient()

    def test_required_auth(self):
        """
        Test that authentication is required
        """
        res = self.client.get(POSTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """
    Test that access to protected API is authenticated
    """

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@muteshi.co.ke',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_posts(self):
        """
        Test retrieving list of posts
        """
        # sample post list
        test_post(user=self.user)
        test_post(user=self.user)

        res = self.client.get(POSTS_URL)

        posts = Post.objects.all().order_by('title')
        serializer = PostSerializer(posts, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_posts_limited_to_user(self):
        """
        Test retrieving posts for specific user
        """
        user2 = get_user_model().objects.create_user(
            'other@muteshi.co.ke',
            'pass24638'
        )
        test_post(user=user2)
        test_post(user=self.user)

        res = self.client.get(POSTS_URL)

        posts = Post.objects.filter(author=self.user)
        serializer = PostSerializer(posts, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)
    
    def test_post_slug_unique(self):
        """
        Test that the slug of posts are unique
        """
        post1 = Post.objects.create(author=self.user, title = 'Testing title', content='Testing content')
        post2 = Post.objects.create(author=self.user, title = 'Testing title', content='Testing content')

        self.assertNotEqual(post1.slug,post2.slug)



    def test_details_post_view(self):
        """
        Test viewing a post detail
        """
        post = test_post(user=self.user)
        post.tags.add(test_tag(user=self.user))
        post.category.add(test_category(user=self.user))
        

        url = detail_post_url(post.slug)
        res = self.client.get(url)

        serializer = PostDetailSerializer(post)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_post(self):
        """
        Test creating a new post
        """
        payload = {
            'title': 'Test post',
            'content':'testing content',
        }

        res = self.client.post(POSTS_URL, payload)
    

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        post = Post.objects.get(id=res.data['id'])
        
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(post, key))

    def test_create_post_with_tags(self):
        """
        Test creating a post with tags
        """
        # sample tags
        tag1 = test_tag(user=self.user, name='Tag 1')
        tag2 = test_tag(user=self.user, name='Tag 2')
        payload = {
            'title': 'Test post with two tags',
            'tags': [tag1.id, tag2.id],
            'content':'Testing content'
        }
        res = self.client.post(POSTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        post = Post.objects.get(id=res.data['id'])
        tags = post.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_post_with_category(self):
        """
        Test creating post with categories
        """
        cat1 = test_category(user=self.user, name='Category 1')
        cat2 = test_category(user=self.user, name='Category 2')
        payload = {
            'title': 'Test post with categories',
            'category': [cat1.id, cat2.id],
            'content':'Testing content'
        }

        res = self.client.post(POSTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        post = Post.objects.get(id=res.data['id'])
        categories = post.category.all()
        self.assertEqual(categories.count(), 2)
        self.assertIn(cat1, categories)
        self.assertIn(cat2, categories)

    def test_partial_update_post(self):
        """
        Test updating a post with http patch method
        """
        post = test_post(user=self.user)
        post.tags.add(test_tag(user=self.user))
        new_tag = test_tag(user=self.user, name='Microsoft')

        payload = {
            'title': 'Windows 11 Launch',
            'tags': [new_tag.id]
        }
        url = detail_post_url(post.slug)
        self.client.patch(url, payload)

        post.refresh_from_db()
        self.assertEqual(post.title, payload['title'])
        tags = post.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_post(self):
        """
        Test updating a post with http put method
        """
        post = test_post(user=self.user)
        post.tags.add(test_tag(user=self.user))

        payload = {
            'title': 'Iphone 13',
            'content':'New iphone 13'
        }
        url = detail_post_url(post.slug)
        self.client.put(url, payload)

        post.refresh_from_db()
        self.assertEqual(post.title, payload['title'])
        self.assertEqual(post.content, payload['content'])
        tags = post.tags.all()
        self.assertEqual(len(tags), 0)


# class RecipeImageUploadTests(TestCase):
#     """
#     Test class for recipe model image upload
#     """

#     def setUp(self):
#         self.client = APIClient()
#         self.user = get_user_model().objects.create_user('user', 'testpass')
#         self.client.force_authenticate(self.user)
#         self.recipe = test_recipe(user=self.user)

#     def tearDown(self):
#         """
#         Clean up function (for removing temp files)
#         """
#         self.recipe.image.delete()

#     def test_upload_image_to_recipe(self):
#         """
#         Test successful uploading of an image to recipe model
#         """
#         url = image_upload_url(self.recipe.id)
#         # named temp file
#         with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
#             img = Image.new('RGB', (10, 10))
#             img.save(ntf, format='JPEG')
#             ntf.seek(0)
#             res = self.client.post(url, {'image': ntf}, format='multipart')

#         self.recipe.refresh_from_db()
#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertIn('image', res.data)
#         self.assertTrue(os.path.exists(self.recipe.image.path))

#     def test_upload_image_bad_request(self):
#         """
#         Test uploading an invalid or empty image
#         """
#         url = image_upload_url(self.recipe.id)
#         res = self.client.post(url, {'image': 'notimage'}, format='multipart')

#         self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

#     def test_filter_recipes_by_tags(self):
#         """
#         Test filtering recipes with specific tag
#         """
#         recipe1 = test_recipe(user=self.user, title='Recipe test 1')
#         recipe2 = test_recipe(user=self.user, title='Recipe test 2')
#         recipe3 = test_recipe(user=self.user, title='Recipe test 3')
#         tag1 = test_tag(user=self.user, name='Test tag 1')
#         tag2 = test_tag(user=self.user, name='Test tag 2')
#         recipe1.tags.add(tag1)
#         recipe2.tags.add(tag2)

#         res = self.client.get(
#             RECIPES_URL,
#             {'tags': '{},{}'.format(tag1.id, tag2.id)}
#         )
#         serializer1 = RecipeSerializer(recipe1)
#         serializer2 = RecipeSerializer(recipe2)
#         serializer3 = RecipeSerializer(recipe3)
#         self.assertIn(serializer1.data, res.data)
#         self.assertIn(serializer2.data, res.data)
#         self.assertNotIn(serializer3.data, res.data)

#     def test_filter_recipes_by_ingredients(self):
#         """
#         Test filtering recipes with specific ingredient
#         """
#         recipe1 = test_recipe(user=self.user, title='Recipe test 4')
#         recipe2 = test_recipe(user=self.user, title='Recipe test 5')
#         recipe3 = test_recipe(user=self.user, title='Recipe test 6')
#         ingredient1 = test_ingredient(
#             user=self.user, name='Test ingredient 6')
#         ingredient2 = test_ingredient(
#             user=self.user, name='Test ingredient 7')
#         recipe1.ingredients.add(ingredient1)
#         recipe2.ingredients.add(ingredient2)

#         res = self.client.get(
#             RECIPES_URL,
#             {'ingredients': '{},{}'.format(ingredient1.id, ingredient2.id)}
#         )
#         serializer1 = RecipeSerializer(recipe1)
#         serializer2 = RecipeSerializer(recipe2)
#         serializer3 = RecipeSerializer(recipe3)
#         self.assertIn(serializer1.data, res.data)
#         self.assertIn(serializer2.data, res.data)
#         self.assertNotIn(serializer3.data, res.data)