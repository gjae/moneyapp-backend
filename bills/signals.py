from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import Bill
from movements.models import Movement


@receiver(post_save, sender=Bill)
def new_bill_has_been_created(sender, instance, created, *args, **kwargs):
    if created:
        fund = instance.pay_from_fund
        Movement.create_movement(
            from_fund=fund,
            to_fund=None,
            subject=f'Pago de factura {instance.bill_number}',
            transaction_id=instance.bill_number,
            amount=instance.total
        )
