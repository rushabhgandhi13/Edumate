# Generated by Django 4.1 on 2023-03-17 11:48

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Student', '0009_submittedassignments_marks'),
    ]

    operations = [
        migrations.AddField(
            model_name='submittedassignments',
            name='sub_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
