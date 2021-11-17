# from django.urls import reverse
# from django.test import TestCase
# from django.core import mail
# from rest_framework.test import APIClient

# from rest_framework import status

# from core.models import Message


# MSG_URL = reverse('blog:message-list')
# mail.outbox = []
# payload = {
#     'name': 'Paul Haha',
#     'email': 'muteshi@muteshi.com',
#     'subject': 'Test subject',
#     'comment': 'comment here',
#     'message_id': 'hha@12345'
# }


# class MessageApiTests(TestCase):
#     """
#     Test messaging feature
#     """

#     def setUp(self) -> None:
#         self.client = APIClient()

#     def test_create_message_successful(self):
#         """
#         Test adding of  new message
#         """
#         self.client.post(MSG_URL, payload)

#         msg = Message.objects.all()
#         self.assertEqual(len(msg), 1)

#     def test_create_message_invalid(self):
#         """
#         Test creating a new message with invalid information
#         """
#         payload = {'name': '', 'email': 'muteshi@muteshi.com',
#                    'subject': 'Test subject',
#                    'comment': 'comment here',
#                    'message_id': 'hha@12345'}  # msg with empty name
#         res = self.client.post(MSG_URL, payload)

#         self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

#     def test_no_email_sent(self):
#         self.client.post(MSG_URL)
#         self.assertEqual(len(mail.outbox), 0)

#     def test_email_sent(self):
#         self.client.post(MSG_URL, payload)
#         self.assertEqual(len(mail.outbox), 1)
#         self.assertEqual(
#             mail.outbox[0].body, 'comment here')
