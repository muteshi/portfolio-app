# Generated by Django 3.2.9 on 2021-11-28 22:26

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.FileField(null=True, upload_to=core.models.post_image_file_path),
        ),
    ]