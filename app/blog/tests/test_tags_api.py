from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Post

from blog.serializers import TagSerializer

TAGS_URL = reverse('blog:tag-list')


def create_test_user(email, password):

    return get_user_model().objects.create_user(email, password)


class PublicTagsApiTests(TestCase):
    """
    Test tags that can be accessed without authentication
    """

    def setUp(self) -> None:
        self.client = APIClient()

    def test_login_required(self):
        """
        Test that a login is required before retrieving user tags
        """
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """
    Test that only authorized user can access protected TAGs
    """

    def setUp(self):
        self.user = create_test_user('muteshi@muteshi.com', 'password')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """
        Test retrieving of tags successfully
        """
        # sample tags
        Tag.objects.create(user=self.user, name='Microsoft')
        Tag.objects.create(user=self.user, name='Twitter')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')  # return tags in order
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """
        Test that tags returned are for the authenticated user
        """
        user2 = create_test_user('muteshi2@gmail.com', 'password')
        Tag.objects.create(user=user2, name='Resume')
        tag = Tag.objects.create(user=self.user, name='Technology')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """
        Test adding of  new tag
        """
        payload = {'name': 'Simple tag'}
        self.client.post(TAGS_URL, payload)

        tag_exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(not tag_exists)

    def test_create_tag_invalid(self):
        """
        Test creating a new tag with invalid information
        """
        payload = {'name': ''}  # tag with empty name
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_retrieve_tags_assigned_to_posts(self):
        """
        Test filtering tags by those assigned to posts
        """
        tag1 = Tag.objects.create(user=self.user, name='Tech')
        tag2 = Tag.objects.create(user=self.user, name='Twitter')
        post = Post.objects.create(
            title='Testing tech title',
            content='Testing again and again',
            author=self.user,
        )
        post.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_tags_assigned_unique(self):
        """
        Test filtering tags by assigned returns unique items
        """
        tag = Tag.objects.create(user=self.user, name='Tech')
        Tag.objects.create(user=self.user, name='Twitter')
        post1 = Post.objects.create(
            title='Testing here bana',
            content='Ha ha ha ha test',
            author=self.user
        )
        post1.tags.add(tag)
        post2 = Post.objects.create(
            title='Testing is good',
            content='Testing i good i say',
            author=self.user
        )
        post2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
