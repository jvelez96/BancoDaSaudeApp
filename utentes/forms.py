from django.forms import ModelForm
from .models import Utente, Partner
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Div, HTML, Fieldset, ButtonHolder, Submit, Row
from .validate import *

from .bundle import *


def popover_html(label, content):
    return label + ' <i tabindex="0" role="button" data-toggle="popover" data-html="true" \
                            data-trigger="hover" data-placement="top" data-content="' + content + '"> \
                            <span style="font-size: 15px; color: Dodgerblue;" class="fas fa-info-circle"></span></i>'


class UtenteForm(ModelForm):
    class Meta:
        model = Utente
        fields = ('tipo_identificacao', 'numero_identificacao', 'niss', 'nif', 'telemovel', 'telefone', 'email')
        labels = {
            'niss': popover_html('NISS', "Número de identificação da Segurança Social"),
            'nif': popover_html('NIF', "Número de Identificação Fiscal = Número de Contribuinte"),
        }

    def is_valid(self):
        valid = super(UtenteForm, self).is_valid()

        if not valid:
            return False

        n_telemovel = self.cleaned_data['telemovel']
        if not validate_telemovel(n_telemovel):
            self.add_error(None, registo_telemovel_invalido)
        n_telefone = self.cleaned_data['telefone']
        if n_telefone != None:
            if not validate_telefone(n_telefone):
                self.add_error(None, registo_telefone_invalido)

        niss = self.cleaned_data['niss']
        if not validate_niss(niss):
            self.add_error(None, registo_niss_invalido)

        nif = self.cleaned_data['nif']
        if not validate_nif(nif):
            self.add_error(None, registo_nif_invalido)

        tipo_id = self.cleaned_data['tipo_identificacao']
        if tipo_id == 'BI':
            bi = self.cleaned_data['numero_identificacao']
            if not validate_bi(bi):
                self.add_error(None, registo_bi_invalido)
        if tipo_id == 'CC':
            cc = self.cleaned_data['numero_identificacao']
            if not validate_cc(cc):
                self.add_error(None, registo_cc_invalido)

        if len(self.errors) > 0:
            return False
        else:
            return True

    def __init__(self, *args, **kwargs):
        super(UtenteForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Dados Pessoais',
                Div(
                    Div(
                        Div('tipo_identificacao', css_class='col-md-6'),
                        Div('numero_identificacao', css_class='col-md-6'),
                        css_class='row'
                    ),
                    Div(
                        Div('niss', css_class='col-md-6'), Div('nif', css_class='col-md-6'),
                        css_class='row'
                    )
                )
            ),
            HTML('<br>'),
            Fieldset(
                'Contactos',
                Div(
                    Div('telemovel', css_class='col-md-6'), Div('telefone', css_class='col-md-6'),
                    css_class='row'
                ),
                'email'
            ),
            ButtonHolder(
                Submit('submit', 'Registar Utente', css_class='button white pull-right')
            )
        )


class EditUtenteDetailsForm(UtenteForm):
    class Meta:
        model = Utente
        fields = (
            'tipo_identificacao', 'numero_identificacao', 'niss', 'nif', 'telemovel', 'telefone', 'email',
            'numero_utente', 'estado_cartao', 'lote')
        labels = {
            'niss': popover_html('NISS', "Número de identificação da Segurança Social"),
            'nif': popover_html('NIF', "Número de Identificação Fiscal = Número de Contribuinte"),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(UtenteForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Dados Pessoais',
                Row(
                    Field('tipo_identificacao', css_class='col-md-12'),
                    Div(Field('numero_identificacao', css_class='col-md-9'), style='margin-left:35px'),

                    Field('niss', css_class='col-md-9'),
                    Field('nif', css_class='col-md-9'),
                    style='margin-left: 20px'
                )
            ),
            Fieldset(
                'Contactos',
                Row(
                    Field('telemovel', css_class='col-md-10'),
                    Field('telefone', css_class='col-md-10'),
                    Field('email', css_class='col-md-13'),
                    style='margin-left: 20px'
                )
            ),
            Fieldset(
                'Dados do Banco da Saúde',
                Row(
                    Field('estado_cartao', css_class='col-md-12'),
                    Div(Field('numero_utente', css_class='col-md-10'), style='margin-left:35px'),
                    Field('lote', css_class='col-md-9'),
                    style='margin-left: 20px'
                )
            ),
            HTML('<br>'),
            Row(
                ButtonHolder(
                    Submit('submit', 'Guardar', css_class='btn btn-outline-info row-md-3 offset-md-0')
                ),
                ButtonHolder(
                    HTML(
                        """<a href="{% url 'utentes:consult_client' %}" class="btn btn-outline-info row-md-2 offset-md-1">Cancelar</a>""")
                ),
                style='margin-left: 20px'
            )
        )

        if not user.groups.filter(name='STAFF').exists():
            del self.fields['lote']
            del self.helper.layout[2][0][2]  # Deletes "Field('lote', css_class='col-md-9')" from layout
            # Changes "estado_cartao" options to: "Entregue" and the current option from the current user
            self.fields['estado_cartao'].choices = list(set([('entregue', 'Entregue'), (self.initial['estado_cartao'], self.instance.get_estado_cartao_display())]))



class PartnerForm(ModelForm):
    class Meta:
        model = Partner
        fields = '__all__'

    def is_valid(self):
        valid = super(PartnerForm, self).is_valid()
        if not valid:
            return False
        return True

    def __init__(self, *args, **kwargs):
        super(PartnerForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Dados Parceiro',
                Div(
                    Div(
                        Div('nome', css_class='col-md-6'),
                        Div('morada', css_class='col-md-6'),
                        css_class='row'
                    )
                )
            ),
            HTML('<br>'),
            Fieldset(
                'Dados Contacto do Parceiro',
                Div(
                    Div('contact_name', css_class='col-md-6'),
                    Div('contact_email', css_class='col-md-6'),
                    Div('contact_phone', css_class='col-md-6'),
                    css_class='row'
                ),
                'email',
                Field('postal_codes', type="hidden"),
                Div('', id="ListOfPostalCodes"),
                HTML("""<div class="input-group mb-3">
                                    <input type="text" id="textCodigopostal" class="form-control" placeholder="Adicionar Codigo-Postal" aria-label="" aria-describedby="basic-addon2">
                                    <div class="input-group-append">
                                        <button class="btn btn-outline-secondary" type="button" onclick="addItem();">Adicionar</button>
                                    </div>
                        </div>
                         """
                ),
            ),
            Div(
                ButtonHolder(
                    Submit('submit', 'Guardar', css_class='button white col')
                ),'&nbsp',
                ButtonHolder(
                    Submit('cancel', 'Cancelar', css_class='button white pull-right col offset-1')
                ), css_class='row')
        )
