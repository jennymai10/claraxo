# Generated by Django 4.2.1 on 2023-10-03 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clara_app', '0022_humanaudioinfo_manual_align_metadata_file_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='humanaudioinfo',
            name='audio_file',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='humanaudioinfo',
            name='manual_align_metadata_file',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]