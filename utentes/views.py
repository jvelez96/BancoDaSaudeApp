from django.shortcuts import get_object_or_404, render, HttpResponse, HttpResponseRedirect, redirect
from django.urls import reverse
from django.views import generic
from .tables import UtenteTable, PartnerTable
from django_tables2 import RequestConfig
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.contrib import messages
from .models import Utente, Lote, Partner
from .forms import UtenteForm, EditUtenteDetailsForm, PartnerForm
from .eligibility import EligibilityForm
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import xlwt
from django.http import HttpResponse, HttpResponseRedirect

from mx3produto.logging import Logger, AUDIT_ACTIONS

from django.core.mail import send_mail

logger = Logger(__name__)


@login_required
def personal_data(request):
    if request.method == 'GET':
        form = UtenteForm(request.GET)
    if request.method == 'POST':
        form = UtenteForm(request.POST)
        if form.is_valid():
            form.save()
            logger.audit(request, AUDIT_ACTIONS.create, screen="Registar Utente", object="Utente",
                         object_attribute="NIF", object_instance=form.cleaned_data['nif'])
            messages.success(request, "Utente Registado com sucesso.")

            email = open('emails_clientes/registo_utente_sucesso.txt', 'r').read()
            for field in ['tipo_identificacao', 'numero_identificacao', 'nif', 'niss', 'telemovel']:
                email = email.replace('$' + field, str(form.cleaned_data.get(field)))

            send_mail("Registado no Banco da Saúde", email, "suporte.bancodasaude@gmail.com",
                      [form.cleaned_data.get('email')])

            return redirect('utentes:successful_register')
        else:
            messages.error(request, "Erro ao registar utente. Cumpra os requisitos dos campos.")
    else:
        form = UtenteForm()

    return render(request, 'utentes/personal_data.html', {'form': form})


@login_required
def eligibility_criteria(request):
    if request.method == 'GET':
        form = EligibilityForm()
    elif request.method == 'POST':
        form = EligibilityForm(request.POST)
        if form.is_valid():
            messages.success(request, "Utente elegivel.")
            return redirect('utentes:personal_data')
        else:
            messages.error(request, "Utente não elegível. Utente não cumpre os requisitos no campo")
    else:
        form = EligibilityForm()

    return render(request, 'utentes/eligibility_criteria.html',
                  {'form': form})


@login_required
def consult_client(request):
    # activity logging

    nr_pages = int(request.GET.get('nr_pages', 25))
    page = request.GET.get('page', 1)

    cartao_filter = request.GET.get('cartao_filter', 'todos')

    query = request.GET.get("search")

    user_is_staff = is_staff(request.user)

    if request.method == 'GET' and query:
        try:
            utente_edit = Utente.objects.get(
                Q(nif=query) | Q(niss=query) | Q(email=query) | Q(telemovel=query) | Q(telefone=query) | Q(
                    numero_identificacao=query))
            # activity logging with filter
            logger.audit(request, AUDIT_ACTIONS.read, screen="Edição de utente", object="Utente",
                         object_attribute="nif", object_instance=utente_edit.nif)

            return redirect('utentes:client_details', id=utente_edit.id)
        except (Utente.DoesNotExist, ValueError):
            logger.audit(request, AUDIT_ACTIONS.read, screen="Consultar Utentes", object="Utentes",
                         other="Filtro usado: " + query)
            istekler = UtenteTable(Utente.objects.all())
    else:
        if cartao_filter == 'todos':
            logger.audit(request, AUDIT_ACTIONS.read, screen="Consultar Utentes", object="Utentes",
                         other="Filtro usado: Estado do Cartão - Todos")
            istekler = UtenteTable(Utente.objects.all())
        else:
            logger.audit(request, AUDIT_ACTIONS.read, screen="Consultar Utentes", object="Utentes",
                         other="Filtro usado: Estado do Cartão - " + cartao_filter)
            istekler = UtenteTable(Utente.objects.filter(Q(estado_cartao=cartao_filter)))

    RequestConfig(request).configure(istekler)

    export = request.GET.get("export")
    if request.method == 'GET' and export and is_staff(request.user):
        qs = Utente.objects.filter(Q(estado_cartao='por pedir'))
        if qs:
            lote = Lote()
            lote.save()
            qs.update(lote=lote)
            logger.audit(request, AUDIT_ACTIONS.create, screen="Consultar Utentes", object="Utentes",
                         other="Exporte de cartões com sucesso - Lote: " + str(lote.numero_lote))
            response = HttpResponse(content_type='application/ms-excel')

            response['Content-Disposition'] = 'attachment; filename="UtentesPorPedir.xls"'

            wb = xlwt.Workbook(encoding='utf-8')
            ws = wb.add_sheet('Users')

            # Sheet header, first row
            row_num = 0

            font_style = xlwt.XFStyle()
            font_style.font.bold = True

            columns = ['NIFF', 'NISS', 'Tipo Identificação', 'Numero Identificação', 'Email', 'Telemovel', 'Telefone',
                       'Lote']

            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)

            # Sheet body, remaining rows
            font_style = xlwt.XFStyle()

            rows = qs.values_list('nif', 'niss', 'tipo_identificacao', 'numero_identificacao', 'email', 'telemovel',
                                  'telefone', 'lote'
                                  )

            for row in rows:
                row_num += 1
                for col_num in range(len(row)):
                    ws.write(row_num, col_num, row[col_num], font_style)

            wb.save(response)

            qs.update(estado_cartao='pedido')

            return response
        else:
            logger.audit(request, AUDIT_ACTIONS.read, screen="Consultar Utentes", object="Utentes",
                         other="Exporte de cartões falhado (Não existem cartões por pedir)")
            export_alert = True

    try:
        istekler.paginate(page=page, per_page=nr_pages)
    except PageNotAnInteger:
        istekler.paginator.page(1)
    except EmptyPage:
        istekler.paginate(page=istekler.paginator.num_pages, per_page=nr_pages)

    return render(request, 'utentes/consult_client.html', locals())


# class ClientDetails(generic.edit.UpdateView):
#     model = Utente
#     form_class = EditUtenteDetailsForm
#     success_url = '/consulta/cliente'
#     template_name = 'utentes/client_details.html'
#
#     @method_decorator(login_required)
#     def dispatch(self, *args, **kwargs):
#         return super().dispatch(*args, **kwargs)

@login_required
def consult_client_details(request, id):
    if request.method == 'POST':
        utente = Utente.objects.get(id=id)

        form = EditUtenteDetailsForm(request.POST, instance=utente, user=request.user)

        if form.is_valid():
            form.save()
            for val in form.changed_data:
                logger.audit(request, AUDIT_ACTIONS.modify, screen="A Editar Utente", object="Utente",
                             object_attribute='NIF', object_instance=utente.nif, changed_attribute=val,
                             old_value=form.initial[val], new_value=form.cleaned_data[val])

            messages.success(request, "Utente editado com sucesso.")
            return redirect('utentes:consult_client')

    if request.method == 'GET':
        test = Utente.objects
        utente = Utente.objects.get(id=id)

        form = EditUtenteDetailsForm(instance=utente, user=request.user)

        logger.audit(request, AUDIT_ACTIONS.read, screen="A Editar Utente", object="Utente",
                     object_attribute='NIF', object_instance=utente.nif)

    return render(request, 'utentes/client_details.html', {'form': form})


def successful_register(request):
    return render(request, 'utentes/successful_register.html')


# Partner Information
@method_decorator(login_required, name='dispatch')
class PartnerCreate(CreateView):
    model = Partner
    form_class = PartnerForm

    # Para o titulo dinamico trocar entre Criar e Alterar
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Criar Parceiro"
        return context


@method_decorator(login_required, name='dispatch')
class PartnerUpdate(UpdateView):
    model = Partner
    form_class = PartnerForm

    # Para o titulo dinamico trocar entre Criar e Alterar
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Actualizar Parceiro"
        return context


@login_required
def consult_partner(request):
    # activity logging
    if (request.user.is_superuser):
        pass  # logger.audit(request, AUDIT_ACTIONS.consult, "User List", "Consulta de utilizadores (modo superuser)")
    else:
        pass  # logger.audit(request, AUDIT_ACTIONS.consult, "User List", "Consulta de utilizadores ")

    nr_pages = int(request.GET.get('nr_pages', 25))
    page = request.GET.get('page', 1)

    # Busca os objectos do form
    query = request.GET.get("search")

    if request.method == 'GET' and query:
        try:
            # TODO: actualizar com os novos campos do form de pesquisa
            partner_edit = Partner.objects.get(
                Q(nome=query) | Q(morada=query) | Q(contact_name=query) | Q(contact_email=query) | Q(
                    contact_phone=query))
            # activity logging with filter

            if request.user.is_superuser:
                pass  # logger.audit(request, AUDIT_ACTIONS.consult, "Partner List",
                # "Consulta por Partners com filtro (modo superuser)", other="Filtro usado: " + query)
            else:
                pass  # logger.audit(request, AUDIT_ACTIONS.consult, "Partner List", "Consulta de utilizadores com filtro",
                # other="Filtro usado: " + query)
            return redirect('utentes:partner_form', pk=partner_edit.id)
        except (Partner.DoesNotExist, ValueError):
            istekler = PartnerTable(Partner.objects.all())
    else:
        istekler = PartnerTable(Partner.objects.all())

    RequestConfig(request).configure(istekler)

    try:
        istekler.paginate(page=page, per_page=nr_pages)
    except PageNotAnInteger:
        istekler = paginator.page(1)
    except EmptyPage:
        istekler.paginate(page=istekler.paginator.num_pages, per_page=nr_pages)

    return render(request, 'utentes/consult_partner.html', locals())


def is_staff(user):
    return user.groups.filter(name='STAFF').exists()

def verificacaoCodigosPostal(utente, user):
    utenteCodigoPostal = utente.codigo_postal
    listCodigoPostais = user.partner.postal_codes

    for cp in listCodigoPostais:
        if cp[0:3] == utenteCodigoPostal[0:3] or cp == utenteCodigoPostal:
            return True
    return False
