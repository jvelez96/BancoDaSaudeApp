from django.shortcuts import get_object_or_404, get_list_or_404, render, HttpResponse, HttpResponseRedirect, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import Group
import django_tables2 as tables
from .models import Med, Order, Pharmacy, Freguesy, OrderDetails, Warehouse, Distributor, District, Product
from utentes.models import Utente
from users.models import Profile
from medicamentos.models import Order, OrderDetails
from django.core.exceptions import ObjectDoesNotExist
from django.views import generic
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django_tables2 import RequestConfig
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.urls import reverse

from sequences import get_next_value
from django.db import transaction

from .forms import OrderForm, PhForm, MedForm, SearchClientForm, PhModelForm, PhModelForm_Create, CheckStockForm

from dal import autocomplete

from django.http import Http404
from .forms import PhForm
from .tables import *

from utentes.validate import *

import functools
import operator

from .webservices import order_operation_write

from django.core.mail import send_mail

from mx3produto.logging import Logger, AUDIT_ACTIONS

logger = Logger(__name__)


class MedAutocomplete(autocomplete.Select2ListView):
    def get_list(self):

        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Med.objects.none()

        qs = Med.objects.all()

        if self.q:
            qs = qs.filter(active_principle__istartswith=self.q)

        return sorted(list(set([m.active_principle for m in qs])))


class PhNameAutoComplete(autocomplete.Select2ListView):
    def get_list(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Pharmacy.objects.none()

        qs = Pharmacy.objects.all()

        if self.q:
            qs = qs.filter(nome__icontains=self.q)

        return sorted(list(set([ph.nome for ph in qs])))


class FreguesyAutoComplete(autocomplete.Select2ListView):
    def get_list(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Freguesy.objects.none()

        qs = Freguesy.objects.all()

        if self.q:
            qs = qs.filter(nome__unaccent__icontains=self.q)

        return sorted(list(set([f.nome for f in qs])))

@login_required
def begin_order(request):
    if request.method == 'GET':
        order = request.user.ordersession.order
        ph = request.user.ordersession.ph

        if not order:
            return redirect('medicamentos:client_search')
        elif request.GET.get("new_order")=='True':
            request.user.ordersession.order = None
            request.user.ordersession.ph = None
            request.user.ordersession.save()
            order.delete()

            #FIX audit log on delet probably
            return redirect('medicamentos:client_search')

        elif order and ph:
            url = reverse('medicamentos:meds_search')
        else:
            url = reverse('medicamentos:ph_search')

        
        return render(request,'begin_order.html',{'redirect_url':url,'order':request.user.ordersession.order})

    else:
        return redirect('medicamentos:begin_order')


@login_required
def client_search(request):

    if request.method == 'GET':
        form = SearchClientForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['search_input']
            if query.isdigit():
                match = Utente.objects.filter(
                    Q(nif=query) |
                    Q(niss=query)
                )

                # checks
                if match.count() >= 2:
                    logger.error("Mais de um utente com Nif ou Niss identicos")

                if match and match.count() == 1:
                    order_operation_write()
                    utente = match.first()
                    order = Order(utente=utente)
                    order.save()
                    logger.audit(request, AUDIT_ACTIONS.read, screen="Encomendar Medicamentos", object="Utente",
                                 object_attribute="NIF", object_instance=utente.nif)

                    # request.session['order_id'] = str(order.order_id)
                    # set NEW order on user
                    request.user.ordersession.order = order
                    request.user.ordersession.save()

                    return redirect('medicamentos:ph_search')
                if not match:
                    messages.error(request, 'Não foi encontrado nenhum Utente.')
            elif query:
                query = ""
                print("query esta com coisas")
                print(query)
                form = SearchClientForm()
    else:
        form = SearchClientForm()

    return render(request, 'search_client.html', {'form': form})


@login_required
def meds_search(request):
    med = []
    scan = 0
    scan_med_id = ""
    order_id = request.user.ordersession.order_id
    ph_id = request.user.ordersession.ph_id

    if order_id:
        order = get_object_or_404(Order, order_id=order_id)
    else:
        redirect('medicamentos:client_search')
    # Se clicar em mudar utente
    if request.GET.get("utente_apagar"):
        request.user.ordersession.order = None
        request.user.ordersession.ph = None
        request.user.ordersession.save()
        order.delete()
        return redirect('medicamentos:client_search')

    # se nao tivermos farmacia selecionada
    if not ph_id:
        return redirect(reverse('medicamentos:ph_search'))  # mandar selecionar
    else:
        # buscar a farmacia para apresentar
        ph = get_object_or_404(Pharmacy, pharmacy_id=ph_id)

    if request.method == "GET" and order_id:
        act_principle = request.GET.get("act_principle")
        dosage = request.GET.get("dosage")
        farm_form = request.GET.get("farm_form")
        packaging = request.GET.get("packaging")

        form = MedForm({'act_principle': act_principle, 'dosage': dosage,
                        'farm_form': farm_form, 'packaging': packaging}, request.GET)
        order_details = OrderDetails.objects.filter(order_id=order_id)
        print(order_details.count())
        if 'confirmar' in request.GET and not order_details.count():
            # se confirmar e n tem meds
            messages.error(
                request, "É necessário adicionar pelo menos 1 Medicamento para se fazer uma encomenda")
        elif 'confirmar' in request.GET:

            if not order.state:
                # Finalizar order
                #Verifica se existem medicamentos que não estão em stock e se existem, pergunta se pertende continuar a encomenda sem estes.
                i = 0
                for order_d in OrderDetails.objects.filter(order_id=order_id):
                    if order_d.med.quantity_stock < order_d.quantity:
                        if not request.GET.get("modal"):
                            i = 1
                            return render(request, 'search_meds.html',
                                          {'form': form, 'order_detail': order_details, 'order': order, 'ph': ph,
                                           'modal': True})
                # Se a resposta foi sim, elimina os medicamentos que não estão em stock
                if request.GET.get("modal") == 'True':
                    for order_d in OrderDetails.objects.filter(order_id=order_id):
                        if order_d.med.quantity_stock < order_d.quantity:
                            order_d.delete()
                    # Se a lista de medicamentos ficou vazia, volta para a página anterior e não efectua a encomenda, caso contrário efectua a encomenda
                    if not OrderDetails.objects.filter(order_id=order_id):
                        messages.error(
                            request, "Nenhum medicamento adicionado está em stock, selecione outros medicamentos.")
                        return render(request, 'search_meds.html',
                                      {'form': form, 'order_detail': order_details, 'order': order, 'ph': ph})
                # Se a resposta foi não continua na mesma página e não efectua a encomenda.
                if i:
                    return render(request, 'search_meds.html',
                                  {'form': form, 'order_detail': order_details, 'order': order, 'ph': ph})

                order.state = True
                order.order_no = get_next_value('Order')
                order.save()
                logger.audit(request, AUDIT_ACTIONS.create, screen="Encomendar Medicamentos", object="Encomenda",
                             object_attribute="Número da Encomenda", object_instance=order.order_id)
            else:
                logger.error(
                    "Tried to change order already done. In Confirm_order view")
                raise Http404("Encomenda já finalizada")

            # reset User order session
            request.user.ordersession.order = None
            request.user.ordersession.ph = None
            request.user.ordersession.save()


            messages.success(request, "Encomenda feita com sucesso")

            email = open('emails_clientes/encomenda_sucesso.txt', 'r').read()
            email = email.replace('$nif', str(order.utente.nif)).replace('$farmacia', ph.nome).replace(
                '$local_farmacia', ph.address + ', ' + ph.freguesia.nome)
            for od in order_details:
                med = od.med
                line = '{} * {} em doses de {} em formato {}, cada embalagem com {} unidades'.format(od.quantity,
                                                                                                     med.active_principle,
                                                                                                     med.dosage,
                                                                                                     med.farmaceutical_form,
                                                                                                     med.packaging)
                email += '\n' + line

            #send_mail("Encomenda feita com sucesso", email, "suporte.bancodasaude@gmail.com", [order.utente.email])

            return redirect('medicamentos:client_search')

        elif 'adicionar' in request.GET:
            if form.is_valid():
                if form.cleaned_data['act_principle'] and form.cleaned_data['dosage'] and form.cleaned_data[
                    'farm_form'] and form.cleaned_data['packaging'] and form.cleaned_data['quantity']:
                    med = Med.objects.filter(Q(active_principle__unaccent__icontains=act_principle) & Q(dosage=dosage) & Q(farmaceutical_form=farm_form) & Q(packaging=packaging))

                    #if med[0].quantity_stock < form.cleaned_data['quantity']:  # Out of stock
                        #messages.error(request, 'O medicamento adicionado não se encontra em stock.')

                    order_item, status = OrderDetails.objects.get_or_create(med=med[0], order=order)
                    if status:
                        order_item.quantity = form.cleaned_data['quantity']
                        print("medicamento adicionado:")
                        print(order_item.med.quantity_stock)
                        print(order_item.med.med_id)
                        order_item.save()
                elif scan == 0:
                    messages.error(
                            request, 'Preencha o formulário corretamente para encontrar o medicamento.')
                else:
                    scan = 0
                form = MedForm()
            else:
                messages.error(
                    request, 'Preencha o formulário corretamente para encontrar o medicamento.')

        elif form.is_valid():
            if form.cleaned_data['act_principle']:
                print("valor do form")
                print(form.cleaned_data['act_principle'])
                med = Med.objects.filter(Q(med_id__icontains=act_principle))
                if med:
                    scan_med_id = form.cleaned_data['act_principle']
                    print("valor do scan")
                    print(scan_med_id)
                    data = {
                        'act_principle': med[0].active_principle,
                        'dosage': med[0].dosage,
                        'farm_form': med[0].farmaceutical_form,
                        'packaging': med[0].packaging
                    }
                    form = MedForm(initial=data)
                    form.fields['dosage'].choices = [
                        (med[0].dosage, med[0].dosage)]
                    form.fields['farm_form'].choices = [
                        (med[0].farmaceutical_form, med[0].farmaceutical_form)]
                    form.fields['packaging'].choices = [
                        (med[0].packaging, med[0].packaging)]

        return render(request, 'search_meds.html',
                      {'form': form, 'order_detail': order_details, 'order': order, 'ph': ph})
    else:
        return redirect(reverse('medicamentos:client_search'))


class MedDelete(generic.edit.DeleteView):
    model = OrderDetails
    success_url = '/encomenda/medicamentos'
    template_name = 'med_delete.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


@login_required
def delete_from_order(request, order_detail_id):
    med_to_delete = OrderDetails.objects.filter(pk=order_detail_id)
    if med_to_delete.exists():
        med_to_delete[0].delete()
        messages.info(request, "Medicamento removido com sucesso.")
    return redirect('medicamentos:meds_search')


@login_required
def delete_order(request, order_id):
    order_to_delete = Order.objects.filter(pk=order_id)
    if order_to_delete.exists():
        order_to_delete[0].delete()
        messages.info(request, "A encomenda foi cancelada.")
    return redirect('')


@login_required
def ph_search(request):
    order_id = request.user.ordersession.order_id

    if request.method == "GET" and order_id:

        distritos = request.GET.get("distritos")
        concelhos = request.GET.get("concelhos")
        order = get_object_or_404(Order, order_id=order_id)
        # order_details = OrderDetails.objects.filter(order_id=order_id)

        # Se clicar em mudar utente
        if request.GET.get("utente_apagar"):
            request.user.ordersession.order = None
            request.user.ordersession.ph = None
            request.user.ordersession.save()
            order.delete()
            return redirect('medicamentos:client_search')

        form = PhForm(
            {'distritos': distritos, 'concelhos': concelhos}, request.GET)

        farmacias = []  # empty list for no form

        if form.is_valid() and request.GET:
            farmacias = Pharmacy.objects.filter(
                active=True)  # only active ph search

            if form.cleaned_data['freguesias']:
                farmacias = farmacias.filter(
                    freguesia=form.cleaned_data['freguesias'])
            elif form.cleaned_data['concelhos'] and form.cleaned_data['distritos']:
                farmacias = farmacias.filter(freguesia__in=Freguesy.objects.filter(
                    concelho=form.cleaned_data['concelhos'], district=form.cleaned_data['distritos']))
            elif form.cleaned_data['distritos']:
                farmacias = farmacias.filter(freguesia__in=Freguesy.objects.filter(
                    district=form.cleaned_data['distritos']))

            if form.cleaned_data['nome']:
                # print("sup")
                # farmacias = farmacias.filter(nome__icontains=form.cleaned_data['nome'])
                farmacias = farmacias.filter(
                    nome__unaccent__icontains=form.cleaned_data['nome'])
            if form.cleaned_data['postal_code']:
                farmacias = farmacias.filter(
                    postal_code__icontains=form.cleaned_data['postal_code'])

        # , 'order_details':order_details
        return render(request, 'search_ph.html', {'form': form, 'ph': farmacias, 'order': order})
    elif request.method == "POST" and order_id:
        ph_id = request.POST.get("ph")

        if ph_id:
            order = get_object_or_404(Order, order_id=order_id)
            ph = get_object_or_404(Pharmacy, pharmacy_id=ph_id)

            if not order.state:
                # update order
                order.pharmacy = ph
                order.save()
            else:
                logger.error(
                    "Tried to change order already done. In ph_search")
                raise Http404("Encomenda ja finalizada")

            request.user.ordersession.ph = ph
            request.user.ordersession.save()

            # vai para o next step meds
            return redirect('medicamentos:meds_search')
        else:
            raise Http404("No MyModel matches the given query.")

    else:
        return redirect('medicamentos:client_search')


# needs also special class
# filter for active pharmacies is needed


@login_required
def ph_manager(request):
    if request.method == "POST":

        # ph_id = request.POST.get("ph")
        ph_ids = request.POST.getlist('ph[]')
        print(ph_ids)

        if ph_ids:

            for ph_id in ph_ids:
                try:
                    ph = Pharmacy.objects.get(pharmacy_id=ph_id)
                except ObjectDoesNotExist as e:
                    messages.error(
                        request, 'Um erro ocorreu ao processar as farmacias')
                    logger.error(
                        'Um erro ocorreu ao processar as farmacias, Objecto Nao existe, ph_id:{},{}'.format(ph_id, e))
                except Exception as e:
                    messages.error(
                        request, 'Um erro ocorreu ao processar as farmacias')
                    logger.error(
                        'Um erro ocorreu ao processar as farmacias, Exception, ph_id:{},{}'.format(ph_id, e))

                ph.active = not ph.active  # inverter valor
                ph.save()

        else:
            raise Http404("No Pharmacy matches the given query.")
    # if request.method =="GET":

    distritos = request.GET.get("distritos")
    concelhos = request.GET.get("concelhos")

    form = PhForm(
        {'distritos': distritos, 'concelhos': concelhos}, request.GET)

    farmacias = []  # empty list for no form

    if form.is_valid() and request.GET:
        farmacias = Pharmacy.objects.all()

        if form.cleaned_data['freguesias']:
            farmacias = farmacias.filter(
                freguesia=form.cleaned_data['freguesias'])
        elif form.cleaned_data['concelhos'] and form.cleaned_data['distritos']:
            farmacias = farmacias.filter(freguesia__in=Freguesy.objects.filter(
                concelho=form.cleaned_data['concelhos'], district=form.cleaned_data['distritos']))
        elif form.cleaned_data['distritos']:
            farmacias = farmacias.filter(freguesia__in=Freguesy.objects.filter(
                district=form.cleaned_data['distritos']))

        if form.cleaned_data['nome']:
            # print("sup")
            # farmacias = farmacias.filter(nome__icontains=form.cleaned_data['nome'])
            farmacias = farmacias.filter(
                nome__unaccent__icontains=form.cleaned_data['nome'])
        if form.cleaned_data['postal_code']:
            farmacias = farmacias.filter(
                postal_code__icontains=form.cleaned_data['postal_code'])

    # criar tabela
    table = PharmacyTable(farmacias, order_by="nome")
    RequestConfig(request).configure(table)

    # try:
    # 	table.paginate(page=page, per_page=nr_pages)
    # except PageNotAnInteger:
    # 	table.paginator.page(1)
    # except EmptyPage:
    # 	table.paginate(page=table.paginator.num_pages, per_page=nr_pages)

    return render(request, 'manage_ph.html', {'form': form, 'ph': table})


@login_required
def ph_manager_create(request):
    # instance = get_object_or_404(Pharmacy, id=id)
    form = PhModelForm_Create(request.GET or None)
    if form.is_valid():
        form.save()
        return redirect('medicamentos:ph_manager')
    return render(request, 'manage_create_ph.html', {'form': form})


class PhDetails(generic.edit.UpdateView):
    model = Pharmacy
    form_class = PhModelForm
    success_url = '/encomenda/farmacias/admin'
    template_name = 'ph_details.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class PhDelete(generic.edit.DeleteView):
    model = Pharmacy
    success_url = '/encomenda/farmacias/admin'
    template_name = 'ph_delete.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


@login_required
def order_search(request):
    if request.method == "GET":
        user = request.user
        search = ""
        form = OrderForm(request.GET)

        choices_dict = {
            "1": "niss",
            "2": "nif",
            "3": "numero_identificacao"
        }

        verbose_dict = {
            "1": "NISS do Utente",
            "2": "NIF do Utente",
            "3": "Número de Identificação do Utente"
        }

        encomendas = []
        if Group.objects.get(name="STAFF") in request.user.groups.all() or user.is_superuser:
            encomendas = Order.objects.all()
        else:
            local_zip_code = Profile.objects.all().get(user=user).partner.postal_codes
            pharmacies = Pharmacy.objects.all().filter(postal_code__in=local_zip_code)
            encomendas = Order.objects.all().filter(pharmacy__in=pharmacies)
        columns = []
        if form.is_valid() and request.GET:
            if form.cleaned_data['tipo_utente']:
                u = ("utentes", tables.Column(accessor="utente." + choices_dict[form.cleaned_data['tipo_utente']],
                                              verbose_name="" + verbose_dict[form.cleaned_data['tipo_utente']]))
                columns.append(u)
                if form.cleaned_data['id_utente'] != '':
                    try:
                        if form.cleaned_data['tipo_utente'] == '1' and validate_niss(form.cleaned_data['id_utente']):
                            encomendas = encomendas.filter(
                                utente=Utente.objects.get(niss=form.cleaned_data['id_utente']))
                        elif form.cleaned_data['tipo_utente'] == '2' and validate_nif(form.cleaned_data['id_utente']):
                            encomendas = encomendas.filter(
                                utente=Utente.objects.get(nif=form.cleaned_data['id_utente']))
                        elif form.cleaned_data['tipo_utente'] == '3' and (
                                validate_cc(form.cleaned_data['id_utente']) or validate_bi(
                            form.cleaned_data['id_utente'])):
                            encomendas = encomendas.filter(
                                utente=Utente.objects.get(numero_identificacao=form.cleaned_data['id_utente']))
                        else:
                            encomendas = Order.objects.none()
                            messages.error(request, "Identificação do Utente introduzida é inválida.")
                    except Utente.DoesNotExist:
                        encomendas = Order.objects.none()
                        messages.error(request, "Utente não tem encomendas em seu nome.")
            if form.cleaned_data['id_farmacia'] != '':
                try:
                    encomendas = encomendas.filter(pharmacy=Pharmacy.objects.get(nome=form.cleaned_data['id_farmacia']))
                except ValidationError:
                    encomendas = Order.objects.none()
                    messages.error(request, "Identificação da Farmácia introduzida é inválido.")
                except Pharmacy.DoesNotExist:
                    encomendas = Order.objects.none()
                    messages.error(request, "Farmácia não tem encomendas registadas.")
            if form.cleaned_data['id_encomenda'] != '':
                try:
                    encomendas = encomendas.filter(order_no=form.cleaned_data['id_encomenda'])
                except ValidationError:
                    encomendas = Order.objects.none()
                    messages.error(request, "ID da Encomenda introduzido é inválido.")
                except Order.DoesNotExist:
                    encomendas = Order.objects.none()
                    messages.error(request, "Não existem encomendas com o ID introduzido.")
    p = ("pharmacies", tables.Column(accessor="pharmacy.nome", verbose_name="Nome da Farmácia"))
    columns.append(p)
    o = ("orders", tables.Column(accessor="order_no", verbose_name="Número da Encomenda"))
    columns.append(o)
    columns.append(("states", tables.BooleanColumn(accessor="state", verbose_name="Estado")))
    table = OrderTable(encomendas, extra_columns=columns, order_by="orders")
    logger.audit(request, AUDIT_ACTIONS.read, screen="Consulta Encomenda", object="Encomenda",
                 other="filtros:" + search.join(form.cleaned_data))
    try:
        RequestConfig(request).configure(table)
    except ValidationError:
        messages.error(request, "ID da Encomenda introduzido é inválido.")
    return render(request, 'search_order.html', {'form': form, 'order': table})


def order_meds(request, order_id):
    logger.audit(request, AUDIT_ACTIONS.read, screen="Consulta Encomenda", object="Encomenda", other="")
    if order_id:
        order = Order.objects.all().get(order_id=order_id)

        utente = Utente.objects.all().filter(nif=order.utente.nif)
        farmacia = Pharmacy.objects.all().filter(pharmacy_id=order.pharmacy.pharmacy_id)
        encomenda = Order.objects.all().filter(order_id=order_id)

        encomendasmeds = []

        if order_id:
            encomendasmeds = OrderDetails.objects.all()
            encomendasmeds = encomendasmeds.filter(order_id=order_id)

        tableutente = SmallUtenteTable(utente)
        tablefarmacia = SmallPharmacyTable(farmacia)
        tableorder = SmallOrderTable(encomenda)
        table = OrderMedTable(encomendasmeds)

        RequestConfig(request).configure(tableutente)
        RequestConfig(request).configure(tablefarmacia)
        RequestConfig(request).configure(tableorder)
        RequestConfig(request).configure(table)
        return render(request, 'order_meds.html',
                      {'ordermeds': table, 'infoutente': tableutente, 'infofarmacia': tablefarmacia,
                       'infoencomenda': tableorder})


@login_required
def manage_stock(request):
    if request.method == "GET":

        form = CheckStockForm(request.GET)

        if form.is_valid() and request.GET:
            Columns=[]
            if form.cleaned_data['distributor'] != '':
                warehouses = Warehouse.objects.all()
                distr = form.cleaned_data['distributor']
                #Arranjar maneira de mandar para o template o valor da choice
                print(distr)
                try:
                    warehouses = Warehouse.objects.filter(owner=distr).order_by('w_id')
                except ValidationError:
                    warehouses = Warehouse.objects.none()
                    messages.error(request, "Não existem armazéns desta distribuidora.")
                except Warehouse.DoesNotExist:
                    warehouses = Warehouse.objects.none()
                    messages.error(request, "Não existem armazéns desta distribuidora.")

                tableW = WarehouseTable(warehouses, order_by="warehouses")
                try:
                    RequestConfig(request).configure(tableW)
                except ValidationError:
                    messages.error(request, "Os armazéns escolhidos são inválidos.")

                form = CheckStockForm()
                return render(request, 'manage_stock.html', {'form': form, 'warehouses': tableW, 'wh_owner': warehouses[0]})
            elif form.cleaned_data['warehouse']:
                #arranjar maneira de fazer display do nome deste armazém

                try:
                    products = Product.objects.filter(warehouse=form.cleaned_data['warehouse'])
                    #query still not working
                except ValidationError:
                    products = Product.objects.none()
                    messages.error(request, "Não existe um armazém com esse nome.")
                except Product.DoesNotExist:
                    products = Product.objects.none()
                    messages.error(request, "Não existe um armazém com esse nome.")

                if products:
                    w = ("warehouse", tables.Column(accessor="warehouse.name", verbose_name="Armazém"))
                    Columns.append(w)
                    table = ProdsInWarehouseTable(products, extra_columns=Columns)
                    RequestConfig(request).configure(table)
                    form = CheckStockForm()
                    return render(request, 'manage_stock.html',{'form': form, 'stock_table': table, 'prod_w': products[0]})
                else:
                    messages.error(request, "Naõ existe nenhum produto em stock neste armazẽm")
            elif form.cleaned_data['district']:
                distr = form.cleaned_data['district']
                try:
                    warehouses = Warehouse.objects.filter(district=distr).order_by('w_id')
                except ValidationError:
                    warehouses = Warehouse.objects.none()
                    messages.error(request, "Não existem armazéns neste distrito.")
                except Warehouse.DoesNotExist:
                    warehouses = Warehouse.objects.none()
                    messages.error(request, "Não existem armazéns neste distrito.")

                tableW = WarehouseTable(warehouses, order_by="warehouses")

                try:
                    RequestConfig(request).configure(tableW)
                except ValidationError:
                    messages.error(request, "Os armazéns escolhidos são inválidos.")

                form = CheckStockForm()
                if warehouses:
                    return render(request, 'manage_stock.html', {'form': form, 'warehouses': tableW, 'wh_region':warehouses[0]})
                else:
                    messages.error(request, "Não existem armazéns de Parceiros nesta localidade.")
                    return render(request, 'manage_stock.html',
                              {'form': form, 'warehouses': tableW})
            elif form.cleaned_data['medF']:
                products = Product.objects.filter(med__active_principle__startswith=form.cleaned_data['medF'])
                #products = Product.objects.filter(med__in= Med.objects.filter(active_principle__icontains=form.cleaned_data['medF'])).distinct()
                if products:
                    w = ("warehouse", tables.Column(accessor="warehouse.name", verbose_name="Armazém"))
                    Columns.append(w)
                    table = ProdsInWarehouseTable(products, extra_columns=Columns)
                    RequestConfig(request).configure(table)
                    form = CheckStockForm()
                    return render(request, 'manage_stock.html', {'form':form, 'stock_table': table, 'prod_m':products[0]})
    """
    logger.audit(request, AUDIT_ACTIONS.read, screen="Consulta Stock", object="Armazéns",
                 other="filtros:" + search.join(form.cleaned_data))
    """

    return render(request, 'manage_stock.html', {'form':form})

@login_required
def warehouse_details(request, warehouse_id):
    if warehouse_id:
        warehouse = Warehouse.objects.all().get(pk=warehouse_id)

        if warehouse:
            products = Product.objects.all()

            if products:
                products = products.filter(warehouse=warehouse)
                table = ProdsInWarehouseTable(products)
                RequestConfig(request).configure(table)
                return render(request, 'warehouse_details.html', {'stock_table': table, 'warehouse': warehouse})

    return render(request, 'warehouse_details.html', {'warehouse':warehouse})


# WEBSERVICE API for CRON

from ipware import get_client_ip

def update_db(request):
    # THIS FUNCTION IS DANGEROUS IF OPEN TO THE PUBLIC (POSSIBLE DDOS RISKS)

    #making sure request comes fron cron tasks
    if request.headers["X-Appengine-Cron"]:

        logger.info("update_db: Cron call")

        return HttpResponse("It worked cron is running")
    else:
        return Http404()

