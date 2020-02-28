# Generated by Django 2.1.2 on 2019-03-03 16:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='Data')),
                ('action', models.CharField(choices=[('C', 'Criar'), ('M', 'Modificação'), ('R', 'Leitura'), ('D', 'Remover')], max_length=2, verbose_name='Ação')),
                ('object', models.CharField(blank=True, default='', max_length=254, null=True, verbose_name='Objecto')),
                ('object_attribute', models.CharField(blank=True, default='', max_length=254, null=True, verbose_name='Atributo do Objecto')),
                ('object_instance', models.CharField(blank=True, default='', max_length=254, null=True, verbose_name='Instância do Objecto')),
                ('screen', models.CharField(blank=True, default='', max_length=254, null=True, verbose_name='Ecrã')),
                ('changed_attribute', models.CharField(blank=True, default='', max_length=254, null=True, verbose_name='Atributo Alterado')),
                ('old_value', models.CharField(blank=True, default='', max_length=254, null=True, verbose_name='Valor Anterior')),
                ('new_value', models.CharField(blank=True, default='', max_length=254, null=True, verbose_name='Valor Novo')),
                ('ip', models.CharField(blank=True, default='', max_length=50, null=True, verbose_name='IP')),
                ('other', models.CharField(blank=True, default='', max_length=254, null=True, verbose_name='Outro')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL, verbose_name='Utilizador')),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(default='default.jpg', upload_to='profile_pics')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
