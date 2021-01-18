from django import forms

from .models import Bill


class RegisterBillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = '__all__'

    def clean(self):
        cleaned_data = super(RegisterBillForm, self).clean()
        print(cleaned_data)
        pay_from_fund = cleaned_data['pay_from_fund']

        if pay_from_fund.current_balance < cleaned_data['total']:
            raise forms.ValidationError('No posee disponibilidad para esta factura')

        return cleaned_data