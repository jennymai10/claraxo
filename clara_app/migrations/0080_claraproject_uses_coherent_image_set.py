# Generated by Django 4.2.1 on 2024-05-21 03:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clara_app', '0079_alter_alignedphoneticlexicon_language_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='claraproject',
            name='uses_coherent_image_set',
            field=models.BooleanField(default=False, help_text='Specifies whether the project uses a coherent AI-generated image set.'),
        ),
    ]