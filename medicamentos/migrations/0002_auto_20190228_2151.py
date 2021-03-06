# Generated by Django 2.1.5 on 2019-02-28 21:51

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('medicamentos', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='ID da Encomenda'),
        ),
        migrations.AlterField(
            model_name='order',
            name='state',
            field=models.BooleanField(default=False, verbose_name='Estado'),
        ),
    ]
