from django.db import models
from django.contrib.auth.models import User
from utentes.models import Partner

from medicamentos.models import Order,Pharmacy


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    partner = models.ForeignKey(Partner, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return  self.user.username

"""class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)"""


class OrderSession(models.Model):
    '''OrderSession
    Used to process the Orders in meds (Encomendar Medicamentos)
    '''
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order,null=True,default=None,on_delete=models.DO_NOTHING)
    ph = models.ForeignKey(Pharmacy,null=True,default=None,on_delete=models.DO_NOTHING)

    order_done = models.BooleanField(default=False)

from model_utils import Choices
from django.utils.translation import ugettext as _

AUDIT_CHOICES = Choices(
		('C', 'create', _('Criar')),
		('M', 'modify', _('Modificação')),
		('R', 'read', _('Leitura')),
		('D', 'delete', _('Remover')))

class AuditLog(models.Model):
    date = models.DateTimeField(auto_now_add=True, blank=True,verbose_name="Data")

    user = models.ForeignKey(User,on_delete=models.DO_NOTHING,verbose_name='Utilizador')
    action = models.CharField(max_length=2, choices=AUDIT_CHOICES,verbose_name="Ação")

    object = models.CharField(max_length=254,verbose_name="Objecto",default='', blank = True, null = True)
    object_attribute = models.CharField(max_length=254,default='', blank = True, null = True,verbose_name="Atributo do Objecto")
    object_instance = models.CharField(max_length=254,default='', blank = True, null = True,verbose_name="Instância do Objecto")
	
    screen = models.CharField(max_length=254, default='', blank = True, null = True,verbose_name="Ecrã") # ecra onde acao foi realizada,assumir q pode ser null
	
    changed_attribute = models.CharField(max_length=254,default='', blank = True, null = True,verbose_name="Atributo Alterado")
    old_value = models.CharField(max_length=254, default='', blank = True, null = True,verbose_name="Valor Anterior")
    new_value = models.CharField(max_length=254, default='', blank = True, null = True,verbose_name="Valor Novo")


    ip = models.CharField(max_length=50, default='',blank = True, null = True,verbose_name="IP")
    other = models.CharField(max_length=254, default='', blank = True, null = True,verbose_name="Outro")