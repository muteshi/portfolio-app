from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Skill

from blog.serializers import SkillSerializer

SKILLS_URL = reverse('blog:skill-list')


def create_test_user(email, password):

    return get_user_model().objects.create_user(email, password)


class PrivateSkillsApiTests(TestCase):
    """
    Test that only authorized user can access protected Skills
    """

    def setUp(self):
        self.user = create_test_user('muteshi@muteshi.com', 'password')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_skills(self):
        """
        Test retrieving of skills successfully
        """
        # sample skills
        Skill.objects.create(user=self.user, title='HTML', percentage=5)
        Skill.objects.create(user=self.user, title='CSS', percentage=5)

        res = self.client.get(SKILLS_URL)

        # return skills in order
        skills = Skill.objects.all().order_by('title')
        serializer = SkillSerializer(skills, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
