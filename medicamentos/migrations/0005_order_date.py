# Generated by Django 2.0.5 on 2019-04-14 03:23

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medicamentos', '0004_auto_20190414_0321'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='date',
            field=models.DateField(default=datetime.datetime(2019, 4, 14, 3, 23, 35, 186911)),
        ),
    ]