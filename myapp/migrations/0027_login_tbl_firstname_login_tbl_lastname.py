# Generated by Django 4.2 on 2025-05-31 06:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0026_delete_adduser_login_tbl_block_login_tbl_user_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='login_tbl',
            name='firstname',
            field=models.CharField(default=1, max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='login_tbl',
            name='lastname',
            field=models.CharField(default=1, max_length=25),
            preserve_default=False,
        ),
    ]
