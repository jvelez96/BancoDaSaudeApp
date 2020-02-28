from django import forms
from django.contrib.auth.models import User, Group

from .models import AuditLog,AUDIT_CHOICES
import django_filters

from bootstrap_datepicker_plus import DatePickerInput

class AuditFilter(django_filters.FilterSet):
    # user_id = django_filters.NumberFilter(lookup_expr='exact')
    # actions = django_filters.ModelMultipleChoiceFilter(queryset=AuditLog.objects.values('action').distinct(), # very slow query though
    #     widget=forms.CheckboxSelectMultiple)
    action = django_filters.MultipleChoiceFilter(required=False,widget=forms.CheckboxSelectMultiple,choices=AUDIT_CHOICES)
    screen = django_filters.CharFilter(lookup_expr='icontains',label='Ecrã')
    object = django_filters.CharFilter(lookup_expr='icontains',label='Objecto')
    # date = django_filters.DateFromToRangeFilter(label='Date',widget=DatePicker(
    #         options={
    #             "format": "mm/dd/yyyy",
    #             "autoclose": True
    #         }
    #     ))

    date = django_filters.DateFilter(label='Data',widget=DatePickerInput(options={
                    "format": "DD/MM/YYYY", # moment date-time format
                    "showClose": True,
                    "showClear": True,
                    "showTodayButton": True,
                    "locale":"pt",
                }),input_formats=['%d/%m/%Y'],lookup_expr='icontains'
    )

    class Meta:
        model = AuditLog
        fields = ['user_id']