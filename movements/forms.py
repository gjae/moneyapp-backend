from django import forms

from .models import Movement, AccountFunds


class NewDepositForm(forms.ModelForm):
    class Meta:
        model = Movement
        fields = ('transaction_id', 'amount', 'description', 'funding')



class NewFundingForm(forms.ModelForm):
    initial_balance = forms.DecimalField(
        required=True,
        max_digits=10,
        decimal_places=2
    )

    class Meta:
        model = AccountFunds
        fields = ('account', 'fund_description', )

    def clean(self):
        print(self.cleaned_data)
        print(self.errors)