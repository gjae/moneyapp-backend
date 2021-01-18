from django.db.models import Q
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import ListView, FormView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponseNotFound, HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.contrib import messages

from accounts.models import Account
from .models import Movement, AccountFunds
from .forms import NewDepositForm, NewFundingForm


# Create your views here.

class UserMovements(LoginRequiredMixin, ListView):
    model = Movement
    template_name = 'user_movements.html'
    login_url = reverse_lazy('login_form')
    redirect_field_name = 'login_url'
    context_object_name = 'movimientos'

    def get_queryset(self, *args, **kwargs):
        user = self.request.user

        if user.is_authenticated:
            account = Account.objects.filter(
                Q(owner__id=user.id) & Q(id=self.kwargs.get('account_id'))
            ).first()
            if not account:
                return HttpResponseNotFound()

            return Movement.objects.getMovementsByAccount(account=account)

    def get_context_data(self, *args, **kwargs):
        context = super(UserMovements, self).get_context_data(*args, **kwargs)
        account = Account.objects.get(
            pk=self.kwargs.get('account_id')
        )
        context['account'] = account

        context['balances'] = account.balances

        return context


class DepositView(LoginRequiredMixin, SuccessMessageMixin, FormView):
    template_name = 'new_deposit.html'
    form_class = NewDepositForm
    success_message = 'Transacción guardada correctamente'

    def get_success_url(self):
        return reverse('account_user_movements', args=[
            self.kwargs.get('account_id')
        ])

    def get_form_class(self, *args, **kwargs):
        account = Account.objects.filter(
            Q(owner__id=self.request.user.id) |
            Q(id=self.kwargs.get('account_id'))
        ).first()

        if not account:
            return HttpResponseNotFound()

        return super(DepositView, self).get_form_class(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(DepositView, self).get_context_data(*args, **kwargs)

        context['account_funds'] = Account.objects.get(
            pk=self.kwargs.get('account_id')
        ).account_funds.all()

        return context

    def form_valid(self, form):
        if form.is_valid():
            Movement.create_movement(
                to_fund=form.cleaned_data['funding'],
                from_fund=None,
                amount=form.cleaned_data['amount'],
                subject=form.cleaned_data['description'],
                transaction_id=form.cleaned_data.get('transaction_id', None)
            )

        return super(DepositView, self).form_valid(form)


class FundingListView(LoginRequiredMixin, ListView):
    template_name = 'funding.html'
    login_url = reverse_lazy('login_form')
    redirect_field_name = 'login_url'
    context_object_name = 'funds'

    def get_queryset(self):
        user = self.request.user

        return AccountFunds.objects.getAllFundsByUser(user)


class FundingCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    template_name = 'new_funding.html'
    success_message = 'Fondo registrado exitosamente'
    form_class = NewFundingForm
    model = AccountFunds

    def get_success_url(self):
        return reverse('funds_view')

    def get_context_data(self, *args, **kwargs):
        context = super(FundingCreateView, self).get_context_data(*args, **kwargs)

        context['user_accounts'] = Account.objects.getByUser(
            self.request.user
        )

        return context

    def form_valid(self, form):
        if form.is_valid():
            account = AccountFunds.objects.creaateFundingFor(
                account=form.cleaned_data['account'],
                desc=form.cleaned_data['fund_description'],
                balance=form.cleaned_data['initial_balance']
            )

        messages.success(self.request, self.get_success_message(form.cleaned_data))
        return HttpResponseRedirect(
            self.get_success_url()
        )
