# Generated by Django 4.2.1 on 2024-03-12 23:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clara_app', '0062_alter_userconfiguration_open_ai_api_key'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fundingrequest',
            name='other_purpose',
            field=models.TextField(blank=True, verbose_name='Explain briefly what you want to do and why you cannot use an API key.'),
        ),
        migrations.CreateModel(
            name='Acknowledgements',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short_text', models.TextField(blank=True, help_text='To appear in the footer of every page.', verbose_name='Short Acknowledgements Text')),
                ('long_text', models.TextField(blank=True, help_text='To be included once in the final rendered text.', verbose_name='Long Acknowledgements Text')),
                ('long_text_location', models.CharField(blank=True, choices=[('first_page', 'Bottom of First Page'), ('extra_page', 'Extra Page at End')], max_length=20, verbose_name='Location of Long Acknowledgements')),
                ('project', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='acknowledgements', to='clara_app.claraproject')),
            ],
        ),
    ]