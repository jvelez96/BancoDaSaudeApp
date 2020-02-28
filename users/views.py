from django.shortcuts import render, redirect,get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.core.paginator import Paginator,EmptyPage, PageNotAnInteger
from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from django.db.models import Q,CharField,IntegerField
from django_tables2 import RequestConfig

from django.contrib.auth.models import Group

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, ProfileStaffUpdateForm, UserStaffUpdateForm
from .models import	AuditLog,User
from .tables import AuditTable, AuditListView, UserTable
from .filters import AuditFilter


from mx3produto.logging import Logger,AUDIT_ACTIONS
logger = Logger(__name__)

def default(request):
	 return render(request, 'default.html')

def register(request):
	if request.method == 'POST':
		form = UserRegisterForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data.get('username')
			messages.success(request, "A sua conta foi criada com sucesso! A partir de agora já pode fazer Log In.")
			return redirect('login')
		else:
			messages.error(request, "Erro ao registar. Cumpra os requisitos dos campos.")
	else:
		form = UserRegisterForm()

	context = {
		'form' : form,
	}
	return render(request, 'users/register.html', context)

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'A sua password foi atualizada corretamente!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'users/change_password.html', {
        'form': form
    })

@login_required
def profile(request):
	return render(request, 'users/profile.html')


@login_required
def profile_update(request):
	#print(request.user.groups.all())

	if request.method == 'POST':
		user_form = UserUpdateForm(request.POST, instance=request.user)
		profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

		#Alteracoes para verificacao de staff
		if Group.objects.get(name="STAFF") in request.user.groups.all():
			user_form = UserStaffUpdateForm(request.POST, instance=request.user)
			profile_form = ProfileStaffUpdateForm(request.POST,request.FILES, instance=request.user.profile)

		if user_form.is_valid() and profile_form.is_valid():
			user_form.save()
			profile_form.save()
			messages.success(request, "Perfil atualizado com sucesso.")
			return redirect('profile')
	else:
		user_form = UserUpdateForm(instance=request.user)
		profile_form = ProfileUpdateForm(instance=request.user.profile)
		#Alteracoes para verificacao de staff
		if Group.objects.get(name="STAFF") in request.user.groups.all():
			user_form = UserStaffUpdateForm(instance=request.user)
			profile_form = ProfileStaffUpdateForm(instance=request.user.profile)

	context = {
		'user_form' : user_form,
		'profile_form' : profile_form
	}

	return render(request, 'users/profile_update.html', context)


@login_required
def view_audit_logs(request):

	nr_pages = int(request.GET.get('nr_pages', 25))
	page = request.GET.get('page', 1)
	search_query = request.GET.get('search', '')

	audit_log_query = AuditLog.objects.all() if request.user.is_superuser else AuditLog.objects.filter(user = request.user) #filter only current user if not admin

	if(search_query):

		fields = [x for x in AuditLog._meta.fields if isinstance(x, CharField) or isinstance(x,IntegerField)]
		search_queries = [Q(**{x.name + "__unaccent__icontains" : search_query}) for x in fields]
		q_object = Q()
		for query in search_queries:
			q_object = q_object | query

		results = audit_log_query.filter(q_object)

		audit_log_query = results

	filter_table = AuditFilter(request.GET, queryset=audit_log_query)
	audit_table = AuditTable(filter_table.qs,order_by="-date")
	RequestConfig(request).configure(audit_table)

	try:
		audit_table.paginate(page=page, per_page=nr_pages)
	except PageNotAnInteger:
		audit_table.paginator.page(1)
	except EmptyPage:
		audit_table.paginate(page=audit_table.paginator.num_pages, per_page=nr_pages)

	# activity logging
	last_search = request.session.get('last_search')# get last search value to avoid excessive audit log
	request.session['last_search'] = search_query

	last_filter_user_id = request.session.get('filter_user_id')
	filter_user_id = request.GET.get('user_id',default=None)
	request.session['filter_user_id'] = filter_user_id

	if(request.user.is_superuser):
		if last_search!=search_query or last_filter_user_id!=filter_user_id: # se a query for diferente e q fazemos log
			logger.audit(request,AUDIT_ACTIONS.read,object="Histórico",screen="Histórico",
			other="Procura:'{}',Filtro de utilizador:{}".format(search_query,get_object_or_404(User,id=filter_user_id).username if isinstance(filter_user_id,int) else "Nenhum"))
	else:
		if last_search!=search_query: # se a query for diferente e q fazemos log
			logger.audit(request,AUDIT_ACTIONS.read,object="Histórico",screen="Histórico",
			other="Procura:'{}'".format(search_query))



	return render(request, 'users/audit_history.html',locals())

@login_required
def dashboards(request):
    return render(request, 'users/dashboards.html')

@login_required
def billing_dashboard(request):
    return render(request, 'users/billing_dashboard.html')



@login_required
def consult_user(request):
    # FIXME activity logging
    if (request.user.is_superuser):
        pass #logger.audit(request, AUDIT_ACTIONS.consult, "User List", "Consulta de utilizadores (modo superuser)")
    else:
        pass #logger.audit(request, AUDIT_ACTIONS.consult, "User List", "Consulta de utilizadores ")

    nr_pages = int(request.GET.get('nr_pages', 25))
    page = request.GET.get('page', 1)

    #Busca os objectos do form
    query = request.GET.get("search")

    if request.method == 'GET' and query:
        try:
            #TODO: actualizar com os novos campos do form de pesquisa
            user_edit = User.objects.get(
                Q(username=query) | Q(first_name=query) | Q(last_name=query))
            # activity logging with filter

            if (request.user.is_superuser):
                pass #logger.audit(request, AUDIT_ACTIONS.consult, "Partner List",
                             #"Consulta por Partners com filtro (modo superuser)", other="Filtro usado: " + query)
            else:
                pass #logger.audit(request, AUDIT_ACTIONS.consult, "Partner List", "Consulta de utilizadores com filtro",
                             #other="Filtro usado: " + query)
            return redirect('users:user_form', pk=user_edit.pk)
        except (User.DoesNotExist, ValueError):
            istekler = UserTable(User.objects.all())
    else:
        istekler = UserTable(User.objects.all())

    RequestConfig(request).configure(istekler)

    try:
        istekler.paginate(page=page, per_page=nr_pages)
    except PageNotAnInteger:
        istekler = paginator.page(1)
    except EmptyPage:
        istekler.paginate(page=istekler.paginator.num_pages, per_page=nr_pages)

    return render(request, 'users/consult_user.html', locals())

def user_update(request, pk):
    user_edit = User.objects.get(pk=pk)
    old_partner = user_edit.profile.partner
    if request.method == "POST":
        user_form = UserStaffUpdateForm(request.POST, instance=user_edit)
        profile_form = ProfileStaffUpdateForm(request.POST, request.FILES, instance=user_edit.profile)
        if user_form.is_valid() and profile_form.is_valid():
            if user_edit.profile.partner is None:
                user_edit.profile.partner = old_partner
            profile_form.save()
            user_form.save()
            return redirect('consult_user')
    else:
        user_form = UserStaffUpdateForm(instance=user_edit)
        profile_form = ProfileStaffUpdateForm(request.FILES,instance=user_edit.profile)

    context = {
		'user_edit' : user_edit,
		'user_form': user_form,
		'profile_form': profile_form
	}

    return render(request, 'users/user_form.html', context)
