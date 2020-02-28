import django_tables2 as tables
from .models import Utente, Partner

class UtenteTable(tables.Table):
    class Meta:
        model = Utente
        fields = ('nif', 'niss', 'tipo_identificacao', 'numero_identificacao','email', 'telemovel', 'telefone', 'estado_cartao', 'numero_utente', 'lote')
        row_attrs = {
            'data-id': lambda record: record.id,
            'class': 'clickable-row'
        }

class PartnerTable(tables.Table):
    class Meta:
        model = Partner
        fields = ('nome','morada','contact_name','contact_email','contact_phone')
        row_attrs = {
            'data-id': lambda record: record.pk,
            'class': 'clickable-row'
        }