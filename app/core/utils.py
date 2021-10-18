import string
import random

from django.core.mail import send_mail

from django.conf import settings
from core.models import Message


def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    """
    Util function for generating unique message id
    """
    the_id = "".join(random.choice(chars) for x in range(size))
    try:
        Message.objects.get(message_id=the_id)
        id_generator()
    except Message.DoesNotExist:
        return the_id


def send_email(serializer_data):
    """
    Util function for sending an email
    """
    body = serializer_data['comment']
    subject = serializer_data['subject']
    from_email = serializer_data['email']

    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL,
              [from_email, settings.EMAIL_COPY])
