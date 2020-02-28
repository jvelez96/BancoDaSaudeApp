from django.db import models
from django.contrib.postgres.fields import ArrayField



class Lote(models.Model):
    numero_lote = models.AutoField(primary_key=True)

    def __str__(self):
        return str(self.numero_lote)

class Utente(models.Model):
    nif = models.IntegerField(unique=True)
    niss = models.CharField(max_length=11, default='', unique=True)
    email = models.EmailField(max_length=254, blank=True)
    telemovel = models.IntegerField()
    telefone = models.IntegerField(default=None, blank=True, null=True)
    tipo_identificacao = models.CharField(default='', max_length=2, choices=(
        ('CC', 'Cartão de Cidadão'),
        ('BI', 'Bilhete de Identidade')
    ) 
                                          )
    numero_identificacao = models.CharField(default='', max_length=13)
    estado_cartao = models.CharField(default='por pedir', max_length=12, choices=(
        ('por pedir', 'Por Pedir'),
        ('pedido', 'Pedido'),
        ('produzido', 'Produzido'),
        ('entregue', 'Entregue')
    )
                                     )
    numero_utente = models.CharField(default='', max_length=12, blank=True)
    lote = models.ForeignKey(Lote, on_delete=models.CASCADE, null=True, blank=True)
    reg_date = models.DateTimeField(auto_now_add=True)


class Partner(models.Model):
    #Partner information
    nome = models.CharField(max_length=255, default='')
    morada = models.CharField(max_length=255, default='')
    #Partner contact information
    contact_name = models.CharField(max_length=255, default='')
    contact_email = models.CharField(max_length=255, default='')
    contact_phone = models.IntegerField(null=True)
    #Partner Postal code information
    postal_codes = ArrayField(
        base_field=models.CharField(max_length=8, blank=True)
        ,size=None
    )

    def __str__(self):
        return self.nome

    def get_absolute_url(self):
        return "/"
