from django.urls import path
from django.conf.urls import url

from . import views

app_name = 'medicamentos'
urlpatterns = [
    path('',views.begin_order,name="begin_order"),
    path('utente/', views.client_search, name='client_search'),
    path('medicamentos/', views.meds_search, name='meds_search'),
    path('medicamentos/remover/<int:order_detail_id>', views.delete_from_order, name='med_delete'),
    path('medicamentos/api/autocomplete/', views.MedAutocomplete.as_view(), name='med_autocomplete'),
    path('farmacias/', views.ph_search, name='ph_search'),
    path('farmacias/admin', views.ph_manager, name='ph_manager'),
    path('farmacias/admin/create', views.ph_manager_create, name='ph_manager_create'),
    path('farmacias/api/nome_autocomplete',views.PhNameAutoComplete.as_view(),name='ph_nome_autocomplete'),
    path('farmacias/api/freguesia_autocomplete',views.FreguesyAutoComplete.as_view(),name='freguesia_autocomplete'),
    # path('status/', views.confirm_order, name='confirm_order'),
    #url(r'^medicamentos/remover/(?P<pk>.+)/$', views.MedDelete.as_view(), name="med_delete"),
    url(r'^farmacias/admin/delete/(?P<pk>.+)/$', views.PhDelete.as_view(), name="ph_delete"),
    url(r'^farmacias/admin/(?P<pk>.+)/$', views.PhDetails.as_view(), name="ph_details"),
    path('encomendas/admin', views.order_search, name='order_search'),
    url(r'^encomendas/admin/(?P<order_id>.+)/$', views.order_meds, name="order_meds"),
    path('stock/', views.manage_stock, name='manage_stock'),
    url(r'^stock/admin/(?P<warehouse_id>.+)/$', views.warehouse_details, name="warehouse_details"),
]
