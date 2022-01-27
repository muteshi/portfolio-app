import os
import uuid

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
    PermissionsMixin

from tinymce import models as tinymce_models

from django.conf import settings


def post_image_file_path(instance, filename):
    """
    Function to generate file path for new post file
    """
    file_extension = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{file_extension}'

    if file_extension.upper() == 'JPEG' or file_extension.upper() == 'JPG'\
            or file_extension.upper() == 'PNG'\
            or file_extension.upper() == 'WEBP':
        return os.path.join('uploads/post/', filename)
    return os.path.join('uploads/resume/', filename)


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
    featured = models.BooleanField(default=False, blank=True, null=True)
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


class Message(models.Model):
    """
    Message model
    """

    name = models.CharField(max_length=250)
    email = models.EmailField(max_length=255)
    subject = models.CharField(max_length=255)
    comment = tinymce_models.HTMLField()
    date_sent = models.DateTimeField(auto_now=False, auto_now_add=True)
    message_id = models.CharField(
        max_length=120, default='ABC', unique=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return self.name


class Skill(models.Model):
    """
    Skill model object
    """
    title = models.CharField(max_length=255)
    percentage = models.IntegerField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class Photos(models.Model):
    """
    Photos model object
    """
    title = models.CharField(max_length=120)
    caption = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    image = models.FileField(
        null=True,
        upload_to=post_image_file_path
    )

    class Meta:
        verbose_name_plural = "Photos"

    def __str__(self):
        return self.title


class Post(models.Model):
    """
    Blog post object
    """
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=455, blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    featured = models.BooleanField(default=False, blank=True, null=True)
    content = tinymce_models.HTMLField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)
    date_posted = models.DateTimeField(auto_now=False, auto_now_add=True)
    tags = models.ManyToManyField('Tag')
    category = models.ManyToManyField('Category')
    image = models.FileField(
        null=True,
        upload_to=post_image_file_path
    )

    class Meta:
        ordering = ["title"]
        verbose_name_plural = "Posts"

    def __str__(self):
        return self.title


class Portfolio(Post):
    url = models.URLField(max_length=200)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-date_posted"]


class Resume(models.Model):
    """
    Resume class object
    """

    title = models.CharField(max_length=120)
    resume = models.FileField(null=True, upload_to=post_image_file_path)

    def __str__(self):
        return self.title
