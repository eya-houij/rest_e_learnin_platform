# Generated by Django 5.0 on 2023-12-13 14:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='role',
            field=models.CharField(choices=[('ADMINISTRATOR', 'Administrator'), ('TUTOR', 'Tutor'), ('STUDENT', 'Student')], default='STUDENT'),
        ),
        migrations.DeleteModel(
            name='Role',
        ),
    ]