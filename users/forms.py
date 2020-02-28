from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from utentes.models import Partner
from .models import Profile


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    """workplace = forms.CharField(label="Local de Trabalho",widget=forms.TextInput(attrs={'placeholder': 'Local de Trabalho'}))"""
    first_name = forms.CharField(label="Nome Próprio")
    last_name = forms.CharField(label="Apelido")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super(UserRegisterForm, self).save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        """user.workplace = self.cleaned_data['workplace']"""

        if commit:
            user.save()
        return user

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['username', 'email']




class UserStaffUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name','email']




class ProfileStaffUpdateForm(forms.ModelForm):

    image = forms.ImageField(required=False, label='Fotografia de Perfil')
    partner = forms.ModelChoiceField(Partner.objects.none(), required=False, label='Alterar Parceiro')

    class Meta:
        model = Profile
        fields = ['image','partner']

    def __init__(self, *args, **kwargs):
        super(ProfileStaffUpdateForm, self).__init__(*args, **kwargs)
        self.fields['partner'].queryset = Partner.objects.all()

class ProfileUpdateForm(forms.ModelForm):
    image = forms.ImageField(required=False, label='Fotografia de Perfil')
    class Meta:
        model = Profile
        fields = ['image']
