# Generated by Django 4.2 on 2025-05-16 05:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0007_delete_client'),
    ]

    operations = [
        migrations.CreateModel(
            name='Agent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client_name', models.CharField(max_length=100)),
                ('email_id', models.EmailField(blank=True, max_length=254, null=True)),
                ('contact_number', models.CharField(blank=True, max_length=20, null=True)),
            ],
        ),
    ]
