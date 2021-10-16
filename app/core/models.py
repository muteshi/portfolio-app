import os
import uuid

from django.db import models
from django.db.models.signals import pre_save
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
    PermissionsMixin

from django.utils.text import slugify

from django.conf import settings


def post_image_file_path(instance, filename):
    """
    Function to generate file path for new post image
    """
    image_extension = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{image_extension}'

    return os.path.join('uploads/post/', filename)


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves a new User"""
        if not email:
            raise ValueError('User must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Creates and saves a new super user"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):

    """Custom user model that supports using email instead of username"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Tag(models.Model):
    """
    Tag model to be used for a post tagging
    """
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class Category(models.Model):
    """
    Category model to be used for blog post
    """
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Post(models.Model):
    """
    Blog post object
    """
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, null=True)
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)
    date_posted = models.DateTimeField(auto_now=False, auto_now_add=True)
    tags = models.ManyToManyField('Tag')
    category = models.ManyToManyField('Category')
    image = models.ImageField(
        null=True,
        upload_to=post_image_file_path
    )

    class Meta:
        ordering = ["title"]
        verbose_name_plural = "Posts"

    def __str__(self):
        return self.title


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


pre_save.connect(pre_save_post_reciever, sender=Post)
