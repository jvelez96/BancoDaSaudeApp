# Generated by Django 2.0.5 on 2019-04-15 21:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medicamentos', '0008_auto_20190415_1751'),
    ]

    operations = [
        migrations.AlterField(
            model_name='warehouse',
            name='name',
            field=models.CharField(default='', max_length=40),
        ),
    ]
