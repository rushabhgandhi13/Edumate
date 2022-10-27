# Generated by Django 4.1.2 on 2022-10-27 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Teacher', '0002_delete_classteachers'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClassTeachers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('teach_id', models.IntegerField()),
                ('class_code', models.CharField(max_length=10)),
                ('class_name', models.CharField(max_length=40)),
            ],
            options={
                'db_table': 'ClassTeachers',
            },
        ),
    ]
