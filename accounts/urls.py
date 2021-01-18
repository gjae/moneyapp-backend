from django.urls import path, include
from .views import *

urlpatterns = [
    path('', DashboardUser.as_view(), name='dashboard_app'),
    path('cuentas/', include([
        path('', AccountUserView.as_view(), name='user_accounts'),
        path('create/', CreateAccountView.as_view(), name="user_accounts_create"),
        path('<int:pk>/delete', AccountDelete.as_view(), name='user_account_delete'),
        path('<int:pk>/edit', UpdateAccountView.as_view(), name='edit'),
        path('', include('bills.urls'))
    ]))
]
