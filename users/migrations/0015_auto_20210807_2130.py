# Generated by Django 3.2.5 on 2021-08-07 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0014_auto_20210807_1852'),
    ]

    operations = [
        migrations.AddField(
            model_name='optoken',
            name='is_absent',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='optoken',
            name='is_reg_user',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='optoken',
            name='otp',
            field=models.CharField(max_length=6, null=True),
        ),
    ]
