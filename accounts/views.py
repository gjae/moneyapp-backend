from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView, ListView, CreateView, DeleteView, UpdateView

from .forms import NewAccountForm
from .models import *


class DashboardUser(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'
    login_url = '/login'
    redirect_field_name = 'login_url'


class AccountUserView(LoginRequiredMixin, ListView):
    template_name = 'accounts.html'
    model = Account
    login_url = '/login'
    context_object_name = 'accounts'
    redirect_field_name = 'login_url'

    def get_queryset(self):
        return Account.objects.getByUser(
            self.request.user
        )

    def get_context_data(self, *args, **kwargs):
        context = super(AccountUserView, self).get_context_data( *args, **kwargs)
        return context


class CreateAccountView(LoginRequiredMixin, CreateView):
    login_url = '/login'
    redirect_field_name = 'login_url'
    form_class = NewAccountForm
    template_name = 'new_account.html'

    def form_valid(self, form):
        user = self.request.user
        acc = Account(
            owner=user,
            entity=AccountEntityFinancial.objects.get(
                pk=self.request.POST['entity']
            ),
            account_code=self.request.POST['account_code'],
            account_type=self.request.POST['account_type']
        )

        acc.save()
        messages.add_message(self.request, messages.SUCCESS, 'La nueva cuenta ha sido guardada')

        return HttpResponseRedirect(reverse('user_accounts') + '?success=True')


class AccountDelete(LoginRequiredMixin, DeleteView):
    model = Account
    success_url = '/dashboard/cuentas/?success=True'


class UpdateAccountView(LoginRequiredMixin, UpdateView):
    model = Account
    success_url = '/dashboard/cuentas/?success=True'
    template_name = 'account_edit.html'
    form_class = NewAccountForm