# Generated by Django 4.1.4 on 2023-01-09 10:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Edumate_app', '0003_initial'),
        ('Teacher', '0018_quiz_question_options'),
        ('Student', '0006_peerstudents'),
    ]

    operations = [
        migrations.CreateModel(
            name='quiz_marks',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('class_id', models.IntegerField()),
                ('student_responses', models.TextField(null=True)),
                ('correct_responses', models.TextField(null=True)),
                ('total_marks', models.PositiveSmallIntegerField(default=0)),
                ('marks_breakup', models.TextField(null=True)),
                ('quiz', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='Teacher.quiz')),
                ('student', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='Edumate_app.students')),
            ],
        ),
    ]
