# Generated by Django 4.1 on 2023-01-26 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Teacher', '0020_attendance'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='class_id',
            field=models.CharField(default=None, max_length=10),
        ),
        migrations.AddField(
            model_name='attendance',
            name='teacher_id',
            field=models.IntegerField(default=None),
        ),
    ]
