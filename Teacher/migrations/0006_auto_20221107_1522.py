# Generated by Django 3.1.7 on 2022-11-07 09:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Teacher', '0005_assignments_max_marks'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classteachers',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]