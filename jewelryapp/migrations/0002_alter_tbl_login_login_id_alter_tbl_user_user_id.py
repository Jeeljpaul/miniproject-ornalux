# Generated by Django 5.1 on 2024-08-20 04:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jewelryapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tbl_login',
            name='login_id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='tbl_user',
            name='user_id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
