# Generated by Django 4.1 on 2022-11-06 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Teacher', '0004_assignments'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignments',
            name='max_marks',
            field=models.FloatField(default=25),
        ),
    ]