# Generated by Django 3.2.5 on 2021-08-01 11:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_doctorappointment_timeslot'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctorappointment',
            name='patient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.patient'),
        ),
    ]
