from django.apps import AppConfig
from django.db.models.signals import pre_save, post_save, post_delete


class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'

    def ready(self):
        from core.models import Post
        from core.models import Message
        from blog.signals import (
            pre_save_post_reciever,
            blog_post_delete_handler,
            blog_post_save_handler,
            post_save_message_reciever
        )

        post_save.connect(blog_post_save_handler, sender=Post)
        post_delete.connect(blog_post_delete_handler, sender=Post)
        pre_save.connect(pre_save_post_reciever, sender=Post)
        post_save.connect(post_save_message_reciever, sender=Message)
