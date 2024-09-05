# Generated by Django 4.2.1 on 2023-09-25 09:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clara_app', '0020_alter_claraproject_l1_alter_claraproject_l2_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='HumanAudioInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('method', models.CharField(choices=[('record', 'Record'), ('manual_align', 'Manual Align'), ('automatic_align', 'Automatic Align')], max_length=20)),
                ('use_for_segments', models.BooleanField(default=False)),
                ('use_for_words', models.BooleanField(default=False)),
                ('voice_talent_id', models.CharField(blank=True, max_length=200, null=True)),
                ('audio_file', models.FileField(blank=True, null=True, upload_to='audio_files/')),
                ('project', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='human_audio_info', to='clara_app.claraproject')),
            ],
        ),
    ]