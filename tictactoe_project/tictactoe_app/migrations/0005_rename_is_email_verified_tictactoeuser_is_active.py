# Generated by Django 4.2.1 on 2024-09-06 08:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tictactoe_app', '0004_tictactoeuser_is_email_verified_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tictactoeuser',
            old_name='is_email_verified',
            new_name='is_active',
        ),
    ]