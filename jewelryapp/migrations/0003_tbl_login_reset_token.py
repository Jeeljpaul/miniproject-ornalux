# Generated by Django 5.1 on 2024-08-22 02:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jewelryapp', '0002_alter_tbl_login_login_id_alter_tbl_user_user_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='tbl_login',
            name='reset_token',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
