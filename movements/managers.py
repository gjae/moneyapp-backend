from django.contrib.auth.models import User
from django.db.models import Manager
from django.db.models import Sum, Q, Case, When, Value, CharField, QuerySet

from accounts.models import Account
from .exceptions import UserInstanceError


class FundManager(Manager):

    def creaateFundingFor(self, account, desc='Balance general', balance=0.00):
        if not isinstance(account, Account):
            raise ValueError("El parametro account ebe ser un modelo Accoubt"
                             )
        return self.create(
            account=account,
            fund_description=desc,
            current_balance=balance
        )

    def getAllFundsByUser(self, user):
        if not isinstance(user, User):
            raise UserInstanceError("Se requiere una isntancia del modelo user")

        return self.filter(
            account__owner=user
        )

    def balancesByUser(self, user):
        if not isinstance(user, User):
            raise ValueError("el metodo balancesByUser debe recibir una instancia de un usuario")

        return self.filter(account__owner=user).aggregate(
            total_actual=Sum('current_balance'),
            total_gastado=Sum('output_balance'),
            total_ingreso=Sum('input_balance')
        )


class MovementManager(Manager):

    def instanceIfUserModel(self, user) -> User:

        if not isinstance(user, User) and not isinstance(user, int):
            raise UserInstanceError(
                "The user param may be User model instance or int value"
            )

        return  user if isinstance(user, User) else User.objects.get(pk=user)

    def getAllByUser(self, user) -> QuerySet:
        """
        Retorna todos los movimientos de un usuario

        :param user: django.contrib.auth.models.User
        :return: django.db.model.QuerySet
        """
        userObject = self.instanceIfUserModel(user)

        return self.filter(
            Q(funding__account__owner__id=userObject.id) |
            Q(from_account_funds__account__owner__id=userObject.id)
        )

    def movementsByUser(self, user) -> QuerySet:
        """
        Retorna todos los movimientos diferenciados por recibidos y enviados

        :param user: django.contrib.auth.models.User
        :return: django.db.models.QuerySet
        """
        userObject = self.instanceIfUserModel(user)

        return self.getAllByUser(userObject).annotate(
            movement_type=Case(
                When(
                    funding__account__owner__id=userObject.id,
                    then=Value('Recibido')
                ),
                default=Value('Enviado'),
                output_field=CharField()
            )
        )

    def getOnlyReceivedsByUser(self, user) -> QuerySet:
        return self.movementsByUser(user).exclude(
            movement_type='Enviado'
        )

    def getOnlySenderByUser(self, user) -> QuerySet:
        return self.movementsByUser(user).exclude(
            movement_type='Recibido'
        )

    def getMovementsByAccount(self, account):
        fromAccount = None

        if isinstance(account, int):
            fromAccount = account
        elif isinstance(account, Account):
            fromAccount = account.id
        else:
            raise ValueError(
                "Debe proporcionar el ID de una cuenta o la instancia de la cuenta"
            )

        return self.filter(
            Q(funding__account__id=fromAccount) |
            Q(from_account_funds__account__id=fromAccount)
        ).annotate(
            movement_type=Case(
                When(
                    funding__account__id=fromAccount,
                    then=Value('Recibido')
                ),
                default=Value('Enviado'),
                output_field=CharField()
            )
        )