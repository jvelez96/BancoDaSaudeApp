from django import forms
from .bundle import *
from datetime import date
from django.contrib import messages
from django.urls import reverse
from django.views import generic
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, MultiField, Div, HTML, Fieldset, ButtonHolder, Submit
import re

from bootstrap_datepicker_plus import DatePickerInput

class EligibilityForm(forms.Form):
    seguranca_social = forms.BooleanField(required=False, label="Seg. Social",widget=forms.CheckboxInput(attrs={
                    'oninvalid' : 'this.setCustomValidity(\'' + eligibilidade_doc_necessario +  '\')',
                    'oninput' : 'this.setCustomValidity(\'\')'}))
    cg_apos = forms.BooleanField(required=False, label="C.G.Apos.",widget=forms.CheckboxInput(attrs={
                    'oninvalid' : 'this.setCustomValidity(\'' + eligibilidade_doc_necessario + '\')',
                    'oninput' : 'this.setCustomValidity(\'\')'}))
    irs = forms.BooleanField(required=True, label="IRS",widget=forms.CheckboxInput(attrs={
                    'oninvalid' : 'this.setCustomValidity(\'' + eligibilidade_doc_necessario + '\')',
                    'oninput' : 'this.setCustomValidity(\'\')'}))
    bens_imoveis = forms.BooleanField(required=True, label="Não possui Bens Imóveis",widget=forms.CheckboxInput(attrs={
                    'oninvalid' : 'this.setCustomValidity(\'' + eligibilidade_doc_necessario + '\')',
                    'oninput' : 'this.setCustomValidity(\'\')'}))
    patrimonio_movel = forms.FloatField(required=True, widget=forms.NumberInput(attrs={
            'placeholder': '€',
            'class' : 'numberinput form-control',
            'oninvalid' : 'this.setCustomValidity(\'' + eligibilidade_numero_maior_zero + '\')',
            'oninput' : 'this.setCustomValidity(\'\')'}),
            min_value=0)
    patrimonio_mobiliario = forms.FloatField(required=True, widget=forms.NumberInput(attrs={
            'placeholder': '€',
            'class' : 'numberinput form-control',
            'oninvalid' : 'this.setCustomValidity(\'' + eligibilidade_numero_maior_zero + '\')',
            'oninput' : 'this.setCustomValidity(\'\')'}),
            min_value=0)
    rendimento_anual = forms.FloatField(required=True, widget=forms.NumberInput(attrs={
            'placeholder': '€',
            'class' : 'numberinput form-control',
            'oninvalid' : 'this.setCustomValidity(\'' + eligibilidade_numero_maior_zero + '\')',
            'oninput' : 'this.setCustomValidity(\'\')'}),
            min_value=1)
    agregado_familiar = forms.IntegerField(required=True, widget=forms.NumberInput(attrs={
            'placeholder': eligibilidade_agregado_familiar_placeholder,
            'class' : 'numberinput form-control',
            'oninvalid' : 'this.setCustomValidity(\'' + eligibilidade_numero_maior_zero + '\')',
            'oninput' : 'this.setCustomValidity(\'\')'}),
            min_value=1)
    data_nascimento = forms.DateField(initial=date.today, required=True, widget=DatePickerInput(options={
                    "format": "DD/MM/YYYY", # moment date-time format
                    "showClose": True,
                    "showClear": True,
					"locale":"pt",
                }),input_formats=['%d/%m/%Y'])
    freguesia = forms.CharField(max_length=20)
    cod_postal = forms.CharField(max_length=20)

    def __init__(self, *args, **kwargs):
        super(EligibilityForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout (
			Fieldset(
				'Entrega de Documentação/Declarações',
				Div(
					Div(
						Div('seguranca_social',
                            HTML(
                                '<i style="right:25%" class="custom-help-icon far fa-question-circle" data-toggle="popover" data-title="Segurança Social" data-trigger="hover" data-placement="bottom" data-content="Registo da entrega da declaração emitida anualmente pela Segurança Social com o valor da reforma"></i>'
                            ),
                            css_class='col'),
                        Div('cg_apos',
                            HTML(
                                '<i style="right:25%" class="custom-help-icon far fa-question-circle" data-toggle="popover" data-title="Caixa Geral de Aposentações" data-trigger="hover" data-placement="bottom" data-content="Registo da entrega da declaração emitida anualmente pela Caixa Geral de Aposentações com o valor da pensão"></i>'
                            ),
                            css_class='col'),
                        Div('irs',
                            HTML(
                                '<i style="right:50%" class="custom-help-icon far fa-question-circle" data-toggle="popover" data-title="Imposto sobre o Rendimento de Pessoas Singulares" data-trigger="hover" data-placement="bottom" data-content="Registo da entrega da declaração do IRS validada pelas Finanças"></i>'
                            ),
                            css_class='col'),
                        Div('bens_imoveis',
                            HTML(
                                '<i class="custom-help-icon far fa-question-circle" data-toggle="popover" data-trigger="hover" data-placement="bottom" data-content="Registo da existência de Habitações Próprias, de modo a comprovar que o Utente não possui Bens Imóveis à exceção da Residência Própria"></i>'
                            ),
                            css_class='col'),
						css_class='row'
					)
				)
			),
            HTML('<br>'),
            Fieldset(
            	'Residência',
            	Div(
            		Div('freguesia', css_class='col-md-6'), Div('cod_postal', css_class='col-md-6'),
            		css_class = 'row'
            	)
            ),
			HTML('<br>'),
			Fieldset(
				'Bens',
				Div(
					Div('patrimonio_movel',
                        HTML(
                                '<i style="right:25%" class="custom-help-icon far fa-question-circle" data-toggle="popover" data-trigger="hover" data-placement="bottom" data-content="Declaração das Finanças que prove que este património não é superior a 26.145,60€, (60 vezes o valor do indexante de apoios sociais)"></i>'
                        ),
                        css_class='col-md-4'),
                    Div('patrimonio_mobiliario',
                        HTML(
                                '<i style="right:15%" class="custom-help-icon far fa-question-circle" data-toggle="popover" data-trigger="hover" data-placement="bottom" data-content="Declaração das Finanças que prove que este património não é superior a 26.145,60€, (60 vezes o valor do indexante de apoios sociais)"></i>'
                        ),
                        css_class='col-md-4'),
                    Div('rendimento_anual',
                        HTML(
                                '<i style="right:25%" class="custom-help-icon far fa-question-circle" data-toggle="popover" data-trigger="hover" data-placement="bottom" data-content="Valor na declaração de IRS, validada pelas Finanças"></i>'
                        ),
                        css_class='col-md-4'),
					css_class = 'row'
				)
			),
			HTML('<br>'),
			Fieldset(
				'Dados Pessoais',
				Div(
					Div('agregado_familiar',
                        HTML(
                                '<i style="right:50%" class="custom-help-icon far fa-question-circle" data-toggle="popover" data-trigger="hover" data-placement="bottom" data-content="Número de pessoas incluídas na declaração de IRS"></i>'
                        ),
                        css_class='col-md-6'), Div('data_nascimento', css_class='col-md-6'),
					css_class = 'row'
				)
			),
			ButtonHolder(
                Submit('submit', 'Verificar Eligibilidade', css_class='button white pull-right')
            )
		)

    def is_valid(self):
        valid = super(EligibilityForm, self).is_valid()

        if not valid:
            return False

        pat_movel = self.cleaned_data['patrimonio_movel']
        if pat_movel > 26145.60:
            self.add_error(None, eligibilidade_pat_movel)

        pat_mob = self.cleaned_data['patrimonio_mobiliario']
        if pat_mob > 26145.60:
            self.add_error(None, eligibilidade_pat_mob)

        rend_anual = self.cleaned_data['rendimento_anual']
        ag_familiar = self.cleaned_data['agregado_familiar']
        rend_per_capita = ( rend_anual / 14 ) / ag_familiar
        if rend_per_capita > 428.90:
            self.add_error(None, eligibilidade_rend_per_capita)

        today = date.today()
        born = (self.cleaned_data['data_nascimento'])
        idade = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        if idade < 65:
            self.add_error(None, eligibilidade_idade_errada)

        ss_value = self.cleaned_data['seguranca_social']
        cga_value = self.cleaned_data['cg_apos']
        if not ss_value and not cga_value:
            self.add_error(None,eligibilidade_ss_ou_cg)

        codigo_postal = self.cleaned_data['cod_postal']
        matches = re.match(r'[0-9]{4}-[0-9]{3}', codigo_postal)
        if not len(codigo_postal) == 8 or not matches:
	           self.add_error(None,eligibilidade_codigo_postal_invalido)

        if len(self.errors) > 0:
            return False
        else:
            return True
