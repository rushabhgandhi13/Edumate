# Generated by Django 4.1.3 on 2022-11-07 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Teacher', '0006_auto_20221107_1522'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classteachers',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
