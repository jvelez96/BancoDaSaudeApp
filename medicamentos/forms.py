from django import forms
from .models import Med,District,Concelho,Freguesy,Pharmacy, Warehouse, Distributor, Product
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, MultiField, Div, HTML, Fieldset, ButtonHolder, Submit,Row

from dal import autocomplete

class SearchClientForm(forms.Form):
    search_input = forms.CharField(label='Procurar Utente pelo NIF ou NISS:', max_length=150, required=False)
    def __init__(self, *args, **kwargs):
        super(SearchClientForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['search_input'].widget.attrs.update({'autofocus': 'autofocus', 'placeholder': 'Insira aqui o NIF ou o NISS'})
        self.helper.layout =  Layout(
            Fieldset(
                '',
                Div(
                    Div('search_input')
                )
            ),
            ButtonHolder(
                Submit('submit', 'Procurar Utente', css_class='btn btn-outline-info')
            )
        )
    
class MedForm(forms.Form):

    act_principle = forms.CharField(label='Principio Ativo', max_length=150, required = False)
    # act_principle = forms.ModelChoiceField(queryset=Med.objects.all(), label='Principio Ativo', required = False, widget=autocomplete.ListSelect2(url='medicamentos:med_autocomplete',attrs={"onChange":'submit()'}))
    dosage = forms.ChoiceField(label='Dosagem', choices = [(None,'')], widget=forms.Select(attrs={"onChange":'submit()'}),required = False)
    farm_form = forms.ChoiceField(label='Forma', choices = [(None,'')], widget=forms.Select(attrs={"onChange":'submit()'}),required = False)
    packaging = forms.ChoiceField(label='Embalagem', choices = [(None,'')], widget=forms.Select(attrs={"onChange":'submit()'}),required = False)
    quantity = forms.IntegerField(label='Quantidade', required=False)

    def __init__(self, form_choices = None, *args, **kwargs):
        super(MedForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['act_principle'].widget.attrs.update({'autofocus': 'autofocus', 'placeholder': 'Realize o scan'})
        self.helper.layout = Layout(
            Fieldset(
                '',
                Div(
                    Div('act_principle', css_class='col'),
                    Div('dosage', css_class='col'), 
                    Div('farm_form', css_class='col'),
                    Div('packaging', css_class='col'),
                    Div('quantity', css_class='col'), 
                    css_class='row'
                ),
            )
        )
        if form_choices: # if is not null
            if form_choices['act_principle']:
                self.fields['dosage'].choices += [(x.dosage, x.dosage) for x in Med.objects.filter(active_principle=form_choices['act_principle']).order_by('dosage').distinct('dosage')]
            if form_choices['act_principle'] and form_choices['dosage']:
                self.fields['farm_form'].choices += [(x.farmaceutical_form, x.farmaceutical_form) for x in Med.objects.filter(active_principle=form_choices['act_principle'], dosage=form_choices['dosage']).order_by('farmaceutical_form').distinct('farmaceutical_form')]
            if form_choices['act_principle'] and form_choices['dosage'] and form_choices['farm_form']:
                self.fields['packaging'].choices += [(x.packaging, x.packaging) for x in Med.objects.filter(active_principle=form_choices['act_principle'], dosage=form_choices['dosage'], farmaceutical_form=form_choices['farm_form']).order_by('packaging').distinct('packaging')]

class PhForm(forms.Form):
    helper = FormHelper()

    nome = forms.CharField(label='Nome Farmácia', max_length=150,required = False)
    postal_code = forms.CharField(label='Código Postal', max_length=150,required = False)

    distritos = forms.ChoiceField(choices = [(None,'Distrito')],widget=forms.Select(attrs={"onChange":'submit()'}),required = False)
    concelhos = forms.ChoiceField(choices = [(None,'Concelho')],widget=forms.Select(attrs={"onChange":'submit()'}),required = False)
    freguesias = forms.ChoiceField(choices = [(None,'Freguesia')],widget=forms.Select(attrs={"onChange":'submit()'}),required = False)

    def __init__(self, local_choices = None, *args, **kwargs):
        super(PhForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                '',
                Div(
                    Div('nome', css_class='col'),
                    Div('postal_code', css_class='col'),
                    Div('distritos', css_class='col'),
                    Div('concelhos', css_class='col'),
                    Div('freguesias', css_class='col'),
                    css_class='row'
                ),
            )
        )
        self.fields['distritos'].choices += [(x.pk,x.nome) for x in District.objects.all()]
        if local_choices:
            if local_choices['distritos']:
                self.fields['concelhos'].choices += [(x.pk,x.nome) for x in Concelho.objects.filter(district=local_choices['distritos'])]
            if local_choices['distritos'] and local_choices['concelhos']:
                self.fields['freguesias'].choices += [(x.pk,x.nome) for x in Freguesy.objects.filter(district=local_choices['distritos'],concelho=local_choices['concelhos'])]


class PhModelForm(forms.ModelForm):
    # freguesia = forms.ChoiceField(choices = [(None,'Freguesia')],widget=forms.Select(attrs={"onChange":'submit()'}),required = False)
    # freguesia = forms.CharField(label='Freguesia', max_length=150,required = True)
    # freguesia = forms.ModelChoiceField(queryset=Freguesy.objects.all(),empty_label="Select Gender")
    class Meta:
        model = Pharmacy
        fields=['nome','address','postal_code','localidade','freguesia','phone','active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        # self.fields['freguesia'] = forms.ChoiceField(choices=((f.pk, f.nome) for f in Freguesy.objects.all()))

        self.helper.layout = Layout(
            Fieldset(
                "Editar Farmácia:",
                Div(
                    Div('nome', css_class='col'),
                    Div('address', css_class='col'),
                    Div('postal_code', css_class='col'),
                    css_class='row'
                ),
                Div(
                    Div('localidade', css_class='col'),
                    Div('freguesia', css_class='col'),
                    Div('phone', css_class='col'),
                    css_class="row"
                ),
                Div('active', css_class='col'),
            ),
            HTML('<br>'),
            Row(
                ButtonHolder(
                    Submit('submit', 'Guardar', css_class='btn btn-outline-info row-md-3 offset-md-0')
                ),
                ButtonHolder(
                    HTML(
                        """<a href="{% url 'medicamentos:ph_manager' %}" class="btn btn-outline-info row-md-2 offset-md-1">Cancelar</a>""")
                ),
                ButtonHolder(
                    HTML(
                        """<button type="button" data-toggle="modal" data-target="#apagar_modal" class="btn btn-outline-danger row-md-2 offset-md-2">Apagar</button>""")
                ),
                style='margin-left: 20px'
            )
    )

class PhModelForm_Create(PhModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper.layout = Layout(
            Fieldset(
                "Nova Farmácia:",
                Div(
                    Div('nome', css_class='col'),
                    Div('address', css_class='col'),
                    Div('postal_code', css_class='col'),
                    css_class='row'
                ),
                Div(
                    Div('localidade', css_class='col'),
                    Div('freguesia', css_class='col'),
                    Div('phone', css_class='col'),
                    css_class="row"
                ),
                Div('active', css_class='col'),
            ),
            HTML('<br>'),
            Row(
                ButtonHolder(
                    Submit('submit', 'Guardar', css_class='btn btn-outline-info row-md-3 offset-md-0')
                ),
                ButtonHolder(
                    HTML(
                        """<a href="{% url 'medicamentos:ph_manager' %}" class="btn btn-outline-info row-md-2 offset-md-1">Cancelar</a>""")
                ),
                style='margin-left: 20px'
            )
    )


class OrderForm(forms.Form):
    helper = FormHelper()

    id_encomenda = forms.CharField(label='Número da Encomenda:', max_length=150, required=False)
    id_utente = forms.CharField(label='NISS do Utente:', max_length=150, required=False)
    id_farmacia = forms.CharField(label='Nome da Farmácia:', max_length=150, required=False)


    tipo_utente = forms.ChoiceField(label='Procurar por Utente através do seu:', choices=[(None, 'Tipo de Identificação do Utente')], widget=forms.Select(attrs={'onChange':'changeLabel(1, this.value)'}),
                                  required=False)

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                '',
                Div(
                    Div('tipo_utente', css_class='col'),
                    Div('id_utente', css_class='col'),
                    css_class='row'
                ),
                Div(
                    Div('id_encomenda', css_class='col'),
                    Div('id_farmacia', css_class='col'),
                    css_class='row'
                ),
            )
        )
        self.fields['tipo_utente'].choices = [(1, 'NISS'), (2, 'NIF'), (3, 'Número de Identificação')]

class CheckStockForm(forms.Form):
    helper = FormHelper()

    medF = forms.CharField(label='Medicamento', max_length=25, required=False)
    warehouse = forms.ChoiceField(label='Armazém', choices = [(None,'Lista de Armazéns')], widget=forms.Select(attrs={"onChange":'submit()'}), required=False)
    distributor = forms.ChoiceField(label='Distribuidora', choices = [(None,'Lista de Distribuidoras')], widget=forms.Select(attrs={"onChange":'submit()'}), required=False)
    district = forms.ChoiceField(label='Distrito', choices = [(None,'Lista de Distritos')], widget=forms.Select(attrs={"onChange":'submit()'}),required=False)

    def __init__(self, *args, **kwargs):
        super(CheckStockForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                '',
                Div(
                    Div('medF', css_class='col'),
                    Div('warehouse', css_class='col'),
                    Div('distributor', css_class='col'),
                    Div('district', css_class='col'),
                    css_class='row'
                ),
            )
        )
        self.fields['district'].choices += [(x.pk, x.nome) for x in District.objects.all()]
        self.fields['distributor'].choices += [(x.pk, x.company_name) for x in Distributor.objects.all()]
        self.fields['warehouse'].choices += [(x.pk, x.name) for x in Warehouse.objects.all()]