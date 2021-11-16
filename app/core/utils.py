import os
import string
import random

from python_http_client.exceptions import HTTPError

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from django.conf import settings


def id_generator(obj, size=10, chars=string.ascii_uppercase + string.digits):
    """
    Util function for generating unique message id
    """
    the_id = "".join(random.choice(chars) for x in range(size))
    try:
        obj.objects.get(message_id=the_id)
        id_generator()
    except obj.DoesNotExist:
        return the_id


def send_email(obj):
    """
    Util function for sending an email
    """
    to_email = obj.email
    to_mails = [
        (to_email, 'Muteshi Paul'),
        (os.environ.get('EMAIL_COPY'), 'Muteshi Paul')
    ]

    message = Mail(
        from_email=(os.environ.get('DEFAULT_FROM_EMAIL'), 'Muteshi Paul'),
        to_emails=to_mails,
        subject='Message to Muteshi Paul about' + obj.subject,
        html_content='Hello </br><p>This is the copy of your message</p> <p>I will get to you ASAP</p>' + obj.comment)

    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)

    except HTTPError as e:
        print(e.to_dict)
