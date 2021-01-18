from django.db import models

# Create your models here.
from accounts.models import Account
from .exceptions import AccountFundArgumentError
from .managers import FundManager, MovementManager


class AccountFunds(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='account_funds')
    fund_description = models.CharField('Denomínación del fondo', max_length=26, null=True, default='Balance princiap')
    opened_fund_date = models.DateTimeField('Fecha de apertura', auto_now=True)
    current_balance = models.DecimalField('Total disponible', default=0.00, decimal_places=2, max_digits=10)
    output_balance = models.DecimalField('Saldo total usado', default=0.00, decimal_places=2, max_digits=10)
    input_balance = models.DecimalField('Total de saldo recibido', default=0.00, decimal_places=2, max_digits=10)

    objects = FundManager()

    def __str__(self):
        return f'{self.fund_description}'

    def addToBalance(self, amount):
        total = amount
        self.current_balance = self.current_balance + total;
        self.input_balance = self.input_balance + total
        self.save()

        return self

    def subToBalance(self, amount):
        total = amount
        self.current_balance = self.current_balance - total
        self.output_balance = self.output_balance + total
        self.save()

        return self


class Movement(models.Model):
    RECEIVED_DESCRIPTION = 'Recibido'
    SEND_DESCRIPTION = 'Enviado'

    funding = models.ForeignKey(AccountFunds, on_delete=models.CASCADE, related_name='account_fund_movement', null=True)
    from_account_funds = models.ForeignKey(AccountFunds, on_delete=models.CASCADE, related_name="from_account_fund",
                                           null=True)
    transaction_id = models.CharField(max_length=12)
    amount = models.DecimalField('Monto de la transacción', decimal_places=2, max_digits=10)
    amount_before_transaction = models.DecimalField('Total antes de la transaccion', decimal_places=2, max_digits=10)
    amount_after_transaction = models.DecimalField('Total despues de la transacción', decimal_places=2, max_digits=10)
    movement_date_register = models.DateTimeField(auto_now=True)
    description = models.TextField('Adjuntar mensaje al movimiento', null=True, blank=True)

    objects = MovementManager()

    def __str__(self):
        return f'{self.funding.account} - {self.amount}'

    @staticmethod
    def create_movement(from_fund, to_fund, amount, subject="", transaction_id=None, *args, **kwargs):
        if (
            not isinstance(from_fund, AccountFunds) and
            not isinstance(to_fund, AccountFunds)
        ):
            raise AccountFundArgumentError(
                "Se debe el fondo de una cuenta tanto para el envio como para la recepción"
            )

        return Movement.objects.create(
            from_account_funds=from_fund,
            funding=to_fund,
            amount=amount,
            description=subject,
            transaction_id=transaction_id
        )
