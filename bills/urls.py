from django.urls import path, include

from .views import ListBillsByAccount, RegisterBill, NulledBill

urlpatterns = [
    path('<int:account_id>/bills/', include([
        path('',  ListBillsByAccount.as_view(), name='bills_by_account'),
        path('register', RegisterBill.as_view(), name='register_bill'),
        path('<int:bill_id>/nulled', NulledBill.as_view(), name='nulled_bill')
    ]))
]