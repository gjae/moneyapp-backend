from django.db import models

from movements.models import AccountFunds
from .managers import BillModelManager

# Create your models here.

class Bill(models.Model):
    bill_number = models.CharField('Codigo de factura', max_length=50, null=False, blank=False)
    subtotal = models.DecimalField('Sub total de la facutura', decimal_places=2, max_digits=10)
    iva = models.DecimalField('Iva de la factura', decimal_places=2, max_digits=10)
    total = models.DecimalField('Total de la factura', decimal_places=2, max_digits=10)
    pay_from_fund = models.ForeignKey(AccountFunds, on_delete=models.RESTRICT, related_name='account_fund_bills')
    emit_date = models.DateField('Fecha de emision', auto_now=True)

    objects = BillModelManager()

    class Meta:
        indexes = [
            models.Index(fields=['bill_number', ], name='index_bill_number'),
        ]

    def __str__(self):
        return f'{self.bill_number}'
