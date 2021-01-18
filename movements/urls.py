from django.urls import path, include

from .views import *

urlpatterns = [
    path('acoounts/', include([
        path('<int:account_id>/movements', UserMovements.as_view(), name='account_user_movements'),
        path('<int:account_id>/movements/deposit', DepositView.as_view(), name='new_deposit'),
    ])),

    path('funds/', include([
        path('', FundingListView.as_view(), name='funds_view'),
        path('create', FundingCreateView.as_view(), name='funds_form_create')
    ]))
]