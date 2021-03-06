# Generated by Django 2.1.2 on 2019-03-03 16:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Lote',
            fields=[
                ('numero_lote', models.AutoField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Utente',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nif', models.IntegerField(unique=True)),
                ('niss', models.CharField(default='', max_length=11, unique=True)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('telemovel', models.IntegerField()),
                ('telefone', models.IntegerField(blank=True, default=None, null=True)),
                ('tipo_identificacao', models.CharField(choices=[('CC', 'Cartão de Cidadão'), ('BI', 'Bilhete de Identidade')], default='', max_length=2)),
                ('numero_identificacao', models.CharField(default='', max_length=13)),
                ('estado_cartao', models.CharField(choices=[('por pedir', 'Por Pedir'), ('pedido', 'Pedido'), ('produzido', 'Produzido'), ('entregue', 'Entregue')], default='por pedir', max_length=12)),
                ('numero_utente', models.CharField(blank=True, default='', max_length=12)),
                ('lote', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='utentes.Lote')),
            ],
        ),
    ]
