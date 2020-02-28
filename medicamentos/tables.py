import django_tables2 as tables
from .models import Pharmacy, Order, OrderDetails, Warehouse, Product
from utentes.models import Utente

class PharmacyTable(tables.Table):
    class Meta:
        model = Pharmacy
        fields = ('nome','morada','phone')
        row_attrs = {
            'data-id': lambda record: record.pk,
            'class': 'clickable-row'
        }

class OrderTable(tables.Table):
    utentes = tables.Column()
    pharmacies = tables.Column()
    orders = tables.Column()
    states = tables.BooleanColumn()

    class Meta:
        model = Order
        fields = ('orders', 'utentes', 'pharmacies', 'states')
        row_attrs = {
            'data-id': lambda record: record.order_id,
            'class': 'clickable-row'
        }

class SmallUtenteTable(tables.Table):
    class Meta:
        model = Utente
        fields = ('numero_utente', 'numero_identificacao','email', 'telemovel', 'telefone')

class SmallOrderTable(tables.Table):
    class Meta:
        model = Order
        fields = ('order_no', 'state')

class SmallPharmacyTable(tables.Table):
    class Meta:
        model = Pharmacy
        fields = ('nome','morada','phone')

class OrderMedTable(tables.Table):
    ap = tables.Column(accessor='med.active_principle', verbose_name='Príncipio Ativo')
    d = tables.Column(accessor='med.dosage', verbose_name='Dosagem')
    f =  tables.Column(accessor='med.farmaceutical_form', verbose_name='Forma')
    p = tables.Column(accessor='med.packaging', verbose_name='Embalagem')
    quantity = tables.Column(accessor='quantity', verbose_name='Quantidade')

    class Meta:
        model = OrderDetails
        fields = ('ap', 'd', 'f', 'p' ,'quantity')
        row_attrs = {
            'data-id': lambda record: record.pk
        }

class WarehouseTable(tables.Table):
    w_id = tables.Column(accessor='w_id', verbose_name='ID do Armazém')
    w_name = tables.Column(accessor='name', verbose_name='Nome do Armazém')
    w_district = tables.Column(accessor='district.nome', verbose_name='Localização')
    w_owner = tables.Column(accessor='owner', verbose_name='Proprietário')
    class Meta:
        model = Warehouse
        fields = ('w_id', 'w_name', 'w_district')
        row_attrs = {
            'data-id': lambda record: record.pk,
            'class': 'clickable-row'
        }

class ProdsInWarehouseTable(tables.Table):
    act_princ = tables.Column(accessor='med.active_principle', verbose_name='Principio Ativo')
    dosage = tables.Column(accessor='med.dosage', verbose_name='Dosagem')
    farm_form = tables.Column(accessor='med.farmaceutical_form', verbose_name='Forma')
    exp_date = tables.Column(accessor='exp_date', verbose_name='Data de Validade')
    stock = tables.Column(accessor='stock', verbose_name='Quantidade')

    class Meta:
        model = Product
        fields = ('act_princ', 'dosage', 'farm_form', 'exp_date','stock')
        row_attrs = {
            'data-id': lambda record: record.pk,
            'class': 'clickable-row'
        }