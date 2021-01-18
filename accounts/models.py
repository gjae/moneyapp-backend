from django.db import models
from django.db.models import  Q, F, Sum, Case, When
from django.contrib.auth.models import User
from .managers import *


# Create your models here.

class AccountEntityType(models.Model):
    ENTITIES = [
        ('BN', 'Banco nacional'),
        ('BE', 'Banco extranjero'),
        ('WE', 'Waller electronico')
    ]

    entity_type = models.CharField('Tipo de entidad', choices=ENTITIES, max_length=8)

    def __str__(self):
        return f'{self.entity_type}'


class AccountEntityFinancial(models.Model):
    type = models.ForeignKey(AccountEntityType, on_delete=models.CASCADE, related_name='type_of_entity')
    entity_name = models.CharField('Nombre de la entidad', max_length=56)
    entity_name_abbr = models.CharField('Nombre corto', max_length=8, null=True)
    entity_prefix_account = models.CharField('Prefijo de cuenta', max_length=10, null=True, default=None)

    def __str__(self):
        return f'{self.entity_name} - {self.entity_name_abbr}'


class Account(models.Model):
    ACCOUNT_TYPES = [
        ('C', 'Corriente'),
        ('A', 'Ahorro'),
        ('D', 'Divisas')
    ]
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_owner')
    entity = models.ForeignKey(AccountEntityFinancial, on_delete=models.RESTRICT, related_name='account_entity')
    account_code = models.CharField('Número/Codigo de cuenta', max_length=100)
    account_type = models.CharField('Tipo de cuenta', choices=ACCOUNT_TYPES, max_length=3)

    objects = AccountManager()

    class Meta:
        indexes = [
            models.Index(fields=['account_code', 'account_type'])
        ]

    def __str__(self):
        return f'{self.account_type} - {self.entity.entity_prefix_account}-{self.account_code}'

    @property
    def fullAccountCode(self) -> str:
        return f'{self.entity.entity_prefix_account}{self.account_code}'

    @property
    def accountTypeDescription(self) -> str:
        for type in self.ACCOUNT_TYPES:
            if type[0] == self.account_type:
                return type[1]

        return '??'

    @property
    def balances(self):
        return Account.objects.filter(
            id=self.id
        ).aggregate(
            current_balance=Sum('account_funds__current_balance'),
            spent=Sum('account_funds__output_balance'),
            joined=Sum('account_funds__input_balance')
        )