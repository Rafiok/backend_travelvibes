# Generated by Django 4.2.7 on 2024-07-26 07:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_audio_image_ourdetails_portefeuille_remove_user_age_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='number',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
