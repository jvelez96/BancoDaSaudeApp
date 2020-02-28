from django.urls import path
from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

app_name = 'utentes'
urlpatterns = [
    path('registo/dadospessoais/', views.personal_data, name='personal_data'),
    path('registo/elegibilidade/', views.eligibility_criteria, name='eligibility'),
    path('consulta/cliente/', views.consult_client, name="consult_client"),
    url(r'^consulta/cliente/(?P<id>\d+)/$', views.consult_client_details, name="client_details"),
    path('registo/sucesso/', views.successful_register, name="successful_register"),
    path('registo/partner/', views.PartnerCreate.as_view(), name='partner_form'),
    url(r'^consulta/parceiro/(?P<pk>\d+)/$', views.PartnerUpdate.as_view(), name='partner_form'),
    path('consulta/parceiro/', views.consult_partner, name="consult_partner"),
]
