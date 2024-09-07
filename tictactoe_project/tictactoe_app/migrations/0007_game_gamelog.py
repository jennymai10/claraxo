# Generated by Django 4.2.1 on 2024-09-07 10:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tictactoe_app', '0006_alter_tictactoeuser_age'),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('game_id', models.AutoField(primary_key=True, serialize=False)),
                ('player_symbol', models.CharField(default='X', max_length=1)),
                ('ai_symbol', models.CharField(default='O', max_length=1)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('completed', models.BooleanField(default=False)),
                ('winner', models.CharField(blank=True, max_length=1, null=True)),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='GameLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('turn_number', models.IntegerField()),
                ('player', models.CharField(max_length=1)),
                ('cell', models.CharField(max_length=1)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='tictactoe_app.game')),
            ],
        ),
    ]
