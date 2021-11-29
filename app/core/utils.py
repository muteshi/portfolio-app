import os
import string
import random

from django.core.cache import cache

from rest_framework.response import Response

from python_http_client.exceptions import HTTPError
from django.template.loader import render_to_string

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


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
    email_sent_template = "blog/message_send_success.html"
    context = {'msg': obj}
    message_content = render_to_string(email_sent_template, context)
    to_mails = [
        (to_email, 'Muteshi Paul'),
        (os.environ.get('EMAIL_COPY'), 'Muteshi Paul')
    ]

    message = Mail(
        from_email=(os.environ.get('DEFAULT_FROM_EMAIL'),
                    'Muteshi Paul - A Full-Stack Web developer'),
        to_emails=to_mails,
        subject='Message to Muteshi Paul about ' + obj.subject,
        html_content=message_content)

    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        return sg.send(message)

    except HTTPError as e:
        print(e.to_dict)


def caching(slug, serializer_data):
    """
    Util function to implement caching
    """
    cache_key = f"post_details_{slug}"
    data = cache.get(cache_key)
    if data:
        check_cache_validity(data)
    # if we have updated data or no data set cache
    cache.set(cache_key, serializer_data)


def check_cache_validity(data):
    """
    Check if cache data is stale
    """
    date_posted = data.get('date_posted')
    updated_date = data.get('updated')
    if date_posted == updated_date:
        return Response(data)
