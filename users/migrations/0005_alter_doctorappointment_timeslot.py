# Generated by Django 3.2.5 on 2021-08-03 10:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_doctorappointment_patient'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctorappointment',
            name='timeslot',
            field=models.IntegerField(choices=[(0, '10:00–10:30'), (1, '10:30–11:00'), (2, '11:00–11:30'), (3, '11:30–12:00'), (4, '12:00–12:30'), (5, '12:30–13:00'), (6, '14:30–15:00'), (7, '15:00–15:30'), (8, '15:30–16:00'), (9, '16:00–16:30'), (10, '16:30–17:00'), (11, '17:00–17:30'), (12, '17:30–18:00'), (13, '18:00–18:30'), (14, '18:30–19:00')]),
        ),
    ]