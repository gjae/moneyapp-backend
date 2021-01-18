from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

import shortuuid
from .models import AccountFunds, Movement
from accounts.models import Account


@receiver(post_save, sender=Account)
def create_account_default_fund(sender, instance=None, created=False, *args, **kwargs):
    if created:
        AccountFunds.objects.creaateFundingFor(instance)


@receiver(pre_save, sender=Movement)
def new_movement_is_created(sender, instance=None, raw=False, *arg, **kwargs):
    """
    Este signal se encarga de actuaizar los balances de las fondos de las cuentas
    to_fund no puede ser null si from_fund lo es al mismo tiempo

    :param sender:
    :param instance:
    :param raw:
    :param arg:
    :param kwargs:
    :return:
    """
    from_fund = instance.from_account_funds
    to_fund = instance.funding
    total_transfer = instance.amount

    if from_fund is not None:
        if from_fund.current_balance <= total_transfer:
            raise ValueError(
                "La cuenta no posee los fondos suficientes para realizar la operacion"
            )
        from_fund.subToBalance(instance.amount)

    # Si los fondos de recepción (to_fund [campo funding del modelo Movement])
    # esta como null, entonces probablemente esta entrando un gasto
    # en ese caso entonces la variable from_funding (campo from_account_funds del modelo Movement)
    # no puede ser null
    if to_fund is not None:
        instance.amount_before_transaction = to_fund.current_balance
        instance.amount_after_transaction = to_fund.current_balance + instance.amount

    elif to_fund is None:
        instance.amount_before_transaction = from_fund.current_balance
        instance.amount_after_transaction = from_fund.current_balance - instance.amount

    if instance.transaction_id is None:
        instance.transaction_id = shortuuid.uuid()

    if to_fund:
        to_fund.addToBalance(instance.amount)
