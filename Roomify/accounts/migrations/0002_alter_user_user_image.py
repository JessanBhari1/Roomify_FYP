# Generated by Django 5.1.7 on 2025-04-16 04:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='user_image',
            field=models.ImageField(default='img/default_user/default_user.webp', null=True, upload_to='img/user_img'),
        ),
    ]
