# Generated by Django 2.0.5 on 2019-04-14 03:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('medicamentos', '0003_merge_20190402_1017'),
    ]

    operations = [
        migrations.CreateModel(
            name='Distributor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(default='', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exp_date', models.DateField()),
                ('prod_id', models.IntegerField(default=0)),
                ('med', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='medicamentos.Med')),
            ],
        ),
        migrations.CreateModel(
            name='Warehouse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('county', models.CharField(default='', max_length=25)),
                ('warehouse_id', models.IntegerField(default=0)),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='medicamentos.Distributor')),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='warehouse',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='medicamentos.Warehouse'),
        ),
    ]