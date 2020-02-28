# Generated by Django 2.1.2 on 2019-04-18 14:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('medicamentos', '0012_auto_20190417_1911'),
        ('users', '0002_profile_partner'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderSession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_done', models.BooleanField(default=False)),
                ('order', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='medicamentos.Order')),
                ('ph', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='medicamentos.Pharmacy')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]