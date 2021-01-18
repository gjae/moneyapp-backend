from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView

from accounts.models import Account
from movements.models import AccountFunds
from .models import Bill
from .forms import RegisterBillForm


# Create your views here.

class ListBillsByAccount(LoginRequiredMixin, ListView):
    login_url = '/login'
    redirect_field_name = 'login_url'
    model = Bill
    template_name = 'bills_list.html'
    context_object_name = 'bills'
    account = None

    def get_queryset(self):
        user = self.request.user
        self.account = Account.objects.get(pk=self.kwargs['account_id'])
        if self.account.owner.id != user.id:
            messages.error(self.request, "No tiene permiso para accesar a estos datos")
            return HttpResponseRedirect(reverse('user_accounts'))

        return self.model.objects.getByAccount(self.account)

    def get_context_data(self, *args, **kwargs):
        context = super(ListBillsByAccount, self).get_context_data(*args, **kwargs)

        context['account'] = self.account

        return context


class RegisterBill(LoginRequiredMixin, CreateView):
    template_name = 'register_bill.html'
    success_url = reverse_lazy('user_accounts')
    model = Bill
    form_class = RegisterBillForm
    account = None

    def get_context_data(self, **kwargs):
        context = super(RegisterBill, self).get_context_data(**kwargs)
        user = self.request.user
        self.account = Account.objects.get(pk=self.kwargs['account_id'])

        if self.account.owner.id != user.id:
            messages.error(self.request, 'No tiene permiso para realizar esta accion')
            return HttpResponseRedirect(reverse('user_accounts'), status=401)

        context['account'] = self.account
        context['funds'] = self.account.account_funds.all()

        return context