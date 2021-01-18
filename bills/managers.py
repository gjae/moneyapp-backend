from django.db import models
from django.db.models import QuerySet

from accounts.models import Account


class BillModelManager(models.Manager):

    def getByAccount(self, account) -> QuerySet:
        """
        Retorna todas las facturas cargadas a la cuenta :account:
        :param account: cuenta a la que hara la busqueda de las facturas
        :return QuerySet:
        """
        accountId = None

        if isinstance(account, Account):
            accountId = account.id
        elif isinstance(account, int):
            accountId = account
        else:
            raise ValueError("El metodo getByAccount del modelo Bill\
             requiere una cuenta a la que hacer la busqueda")

        return self.filter(
            pay_from_fund__account__id=accountId
        )
