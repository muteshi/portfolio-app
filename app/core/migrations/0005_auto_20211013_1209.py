# Generated by Django 3.2.8 on 2021-10-13 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20211013_1153'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='category',
            field=models.ManyToManyField(to='core.Category'),
        ),
        migrations.AddField(
            model_name='post',
            name='tags',
            field=models.ManyToManyField(to='core.Tag'),
        ),
    ]
