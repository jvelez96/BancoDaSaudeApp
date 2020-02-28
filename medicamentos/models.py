from django.db import models
import utentes.models
from hashid_field import HashidAutoField
import uuid
from datetime import datetime
from django.utils import timezone

class District(models.Model):
    nome = models.CharField(max_length=100, default='', primary_key=True)

class Concelho(models.Model):
    nome = models.CharField(max_length=100, default='', primary_key=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE)

class Freguesy(models.Model):
    nome = models.CharField(max_length=150, default='', primary_key=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    concelho = models.ForeignKey(Concelho, on_delete=models.CASCADE)

class Pharmacy(models.Model):
    pharmacy_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=100, default='')
    address = models.CharField(max_length=100, default='',verbose_name="Morada")
    postal_code = models.CharField(max_length=8, default='',verbose_name="Código Postal")
    localidade = models.CharField(max_length=50, default='')
    phone = models.IntegerField(default=None,null=True,verbose_name="Número de telefone")
    latitude = models.CharField(max_length=50,default='',null=True)
    longitude = models.CharField(max_length=50,default='',null=True)
    freguesia = models.ForeignKey(Freguesy, on_delete=models.CASCADE)
    active = models.BooleanField(default=False,verbose_name="Elegível")

    def morada(self):
        # Custom function for table show
        return "{}, {} {}".format(self.address,self.localidade,self.postal_code)
    def __str__(self):
        return self.nome
    def __unicode__(self):
        return self.nome

class Med(models.Model):
    med_id = models.CharField(default='', max_length=350)
    active_principle = models.CharField(max_length=150, default='')
    dosage = models.CharField(max_length=50, default='')
    farmaceutical_form = models.CharField(max_length=100, default='')
    packaging = models.IntegerField(default=0)
    quantity_stock = models.IntegerField(default=0)
    name = models.CharField(max_length=150, default='')
    cnpem = models.IntegerField(default=0)
    preco = models.DecimalField(default=0, decimal_places=2, max_digits=10)
    preco_notificado = models.DecimalField(default=0, decimal_places=2, max_digits=10)
    preco_utente = models.DecimalField(default=0, decimal_places=2, max_digits=10)
    preco_pensionistas = models.DecimalField(default=0, decimal_places=2, max_digits=10)

    def __str__(self):
        return self.active_principle

class Distributor(models.Model):
    company_name = models.CharField(default='', max_length=20)
    #se não precisarmos de mais informações do distribuidor passa a ser um atributo do warehouse
    def __str__(self):
        return self.company_name

class Warehouse(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    owner = models.ForeignKey(Distributor, on_delete=models.CASCADE, null=True)
    w_id = models.IntegerField(default=0)
    name = models.CharField(default='', max_length=40)

    def __str__(self):
        return self.name

class Product(models.Model):
    med = models.ForeignKey(Med, related_name='med', on_delete=models.CASCADE, null=True)
    warehouse = models.ForeignKey(Warehouse, related_name='warehouse',on_delete=models.CASCADE, null=True)
    exp_date = models.DateField()
    prod_id = models.IntegerField(default=0)
    stock = models.IntegerField(default=0)

    class Meta:
        unique_together=('med','warehouse')

class Order(models.Model):
    description = models.CharField(max_length=100, default='')
    order_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, verbose_name='ID da Encomenda')
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, null=True)
    utente = models.ForeignKey(utentes.models.Utente, on_delete=models.CASCADE, null=True)
    state = models.BooleanField(default=False, verbose_name='Estado')
    order_no = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    def identify_utente(self):
        return "{}".format(self.utente.numero_identificacao)

    def identify_pharmacy(self):
        return "{}".format(self.pharmacy.nome)

class OrderDetails(models.Model):
   quantity = models.IntegerField(default=0)
   order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
   # vai passar a ser product
   med = models.ForeignKey(Med, on_delete=models.DO_NOTHING, null=True)

   def __str__(self):
        return self.med.active_principle

   def identify_med(self):
       return "{}".format(self.med.active_principle)
