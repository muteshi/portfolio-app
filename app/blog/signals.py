from django.core.cache import cache
from django.utils.text import slugify
from core.models import Post

from core.utils import send_email


def create_slug(obj, field, instance, new_slug=None):
    slug = slugify(field)
    if new_slug is not None:
        slug = new_slug
    queryset = obj.objects.filter(slug=slug).order_by("-id")
    exists = queryset.exists()
    if exists:
        new_slug = f'{slug}-{queryset.first().id}'
        return create_slug(obj, field, instance, new_slug=new_slug)
    return slug


def pre_save_post_reciever(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(Post, instance.title, instance)


def post_save_message_reciever(sender, instance, created, *args, **kwargs):

    if created:
        try:
            send_email(instance)
        except Exception as e:
            print(e)


def _invalidate_cached_data(slug):

    cache_key = f"post_details_{slug}"
    cache.delete(cache_key)


def blog_post_save_handler(sender, instance, created, **kwargs):
    if not created:
        _invalidate_cached_data(instance.slug)


def blog_post_delete_handler(sender, instance, **kwargs):
    _invalidate_cached_data(instance.slug)
