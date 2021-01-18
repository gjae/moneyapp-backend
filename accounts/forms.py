from django import forms
from .models import *


class NewAccountForm(forms.ModelForm):

    entity = forms.ModelChoiceField(
        required=True,
        label='Entidad bancaria',
        queryset=AccountEntityFinancial.objects.all(),
        empty_label='Seleccione un banco',
        widget=forms.Select(
            attrs={'class': 'form-control'}
        )
    )

    account_type = forms.ChoiceField(
        required=True,
        label='Tipo de cuenta',
        choices=Account.ACCOUNT_TYPES,
        widget=forms.Select(
            attrs={'class': 'form-control'}
        )
    )

    account_code = forms.CharField(
        max_length=20,
        min_length=5,
        strip=True,
        empty_value='No incluya el prefijo',
        label="Cuenta (no incluya prefijo del banco)",
        widget=forms.TextInput(
            attrs={'class': 'form-control'}
        )
    )

    class Meta:
        model = Account
        fields = ['entity', 'account_type', 'account_code']

