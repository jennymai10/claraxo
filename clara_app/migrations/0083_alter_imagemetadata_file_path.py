# Generated by Django 4.2.1 on 2024-06-04 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clara_app', '0082_imagemetadata_description_variable_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imagemetadata',
            name='file_path',
            field=models.TextField(blank=True, default=''),
        ),
    ]