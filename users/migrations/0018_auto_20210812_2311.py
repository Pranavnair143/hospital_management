# Generated by Django 3.2.5 on 2021-08-12 17:41

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_circular'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Circular',
        ),
        migrations.AddField(
            model_name='doctor',
            name='dob',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
