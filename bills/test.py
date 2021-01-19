from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse

from django.contrib.auth.models import User
from accounts.models import Account, AccountEntityType, AccountEntityFinancial
from movements.models import AccountFunds, Movement
from .models import Bill


class TestBillModel(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@gmail.com',
            username='testuser',
            password='123456789'
        )

        self.accountEntityType = AccountEntityType.objects.create(
            entity_type='BN'
        )

        self.accountEntityTypeFinancial = AccountEntityFinancial.objects.create(
            type=self.accountEntityType,
            entity_name='BANCO DE VENEZUELA',
            entity_name_abbr='BDV',
            entity_prefix_account='0102'
        )

        self.account = Account.objects.create(
            owner=self.user,
            entity=self.accountEntityTypeFinancial,
            account_code='01203401234213',
            account_type='C'
        )

        self.account2 = Account.objects.create(
            owner=self.user,
            entity=self.accountEntityTypeFinancial,
            account_code='01203401234213',
            account_type='C'
        )

    def testBillBelongsToAccount(self):
        fund = self.account.account_funds.first()
        fund.current_balance = 10000
        fund.save()

        bill = Bill.objects.create(
            bill_number='00290012312',
            subtotal=1400,
            iva=100,
            total=1500,
            pay_from_fund=fund
        )
        bills = Bill.objects.all()

        self.assertIsNotNone(bill.pay_from_fund)
        self.assertEqual(len(bills), 1)
        self.assertIsInstance(bill.pay_from_fund, AccountFunds)
        self.assertEqual(bill.pay_from_fund, fund)

    def testGetBillsByAccount(self):
        fund = self.account.account_funds.first()
        fund.current_balance = 10000
        fund.save()

        bill = Bill.objects.create(
            bill_number='00290012312',
            subtotal=Decimal(1400),
            iva=Decimal(100.00),
            total=Decimal(1500.00),
            pay_from_fund=fund
        )

        bills = Bill.objects.getByAccount(self.account)
        billsFromAccount2 = Bill.objects.getByAccount(self.account2)

        self.assertEqual(len(bills), 1)
        self.assertEqual(len(billsFromAccount2), 0)

    def testWhenBillIsCreatedThenAlsoMovementIsCreated(self):
        fund = self.account.account_funds.first()
        fund.current_balance = 10000
        fund.save()

        bill = Bill.objects.create(
            bill_number='00290012312',
            subtotal=Decimal(1400),
            iva=Decimal(100.00),
            total=Decimal(1500.00),
            pay_from_fund=fund
        )

        movements = Movement.objects.all()
        self.assertEqual(len(movements), 1)

    def testWhenBillIsCreatedThenTheFundHasLessBalance(self):
        fund = self.account.account_funds.first()
        fund.current_balance = 10000
        fund.save()

        bill = Bill.objects.create(
            bill_number='00290012312',
            subtotal=Decimal(1400),
            iva=Decimal(100.00),
            total=Decimal(1500.00),
            pay_from_fund=fund
        )

        fund = self.account.account_funds.first()

        self.assertEqual(fund.current_balance, 8500)
        self.assertEqual(fund.output_balance, 1500)
        self.assertEqual(fund.input_balance, 0)


class TestCreateBillByUser(TestBillModel):

    def setUp(self):
        super(TestCreateBillByUser, self).setUp()
        self.client = Client()

    def testWhenUserIsNotLogin(self):
        response = self.client.get(
            reverse('bills_by_account', kwargs={'account_id': self.account.id})
        )

        self.assertGreater(response.status_code, 300)
        self.assertRedirects(
            response,
            f'/login?login_url=/dashboard/cuentas/1/bills/',
            target_status_code=301
        )

    def testCreateBillOnInvalidAccount(self):
        secondaryUser = User.objects.create_user(
            email='user2@gmail.com',
            password='123456789',
            username='test2@gmail.com'
        )
        self.client.login(username=secondaryUser.username, password='123456789')

        response = self.client.get(
            reverse('register_bill', kwargs={'account_id': self.account.id})
        )

        self.assertContains(response, '401 Unhautorized', status_code=401)

    def testUserCreteBill(self):
        self.client.login(username=self.user.username, password='123456789')
        fund = self.account.account_funds.first()
        fund.current_balance = 10000
        fund.save()

        response = self.client.post(
            reverse('register_bill', kwargs={'account_id': self.account.id}),
            {'bill_number': '000001',
             'emit_date': '2020-01-18', 'pay_from_fund': fund.id,
             'subtotal': 1400, 'iva': 100, 'total': 1500}
        )

        bills = Bill.objects.all()
        fund = self.account.account_funds.first()

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse('user_accounts')
        )
        self.assertEqual(fund.current_balance, 8500)
        self.assertEqual(len(bills), 1)

    def testIntentNulledBillsThatNotIsOwnOfUser(self):
        fund = self.account.account_funds.first();
        fund.current_balance = 10000
        bill = Bill.objects.create(
            bill_number='00290012312',
            subtotal=Decimal(1400),
            iva=Decimal(100.00),
            total=Decimal(1500.00),
            pay_from_fund=fund
        )

        secondaryUser = User.objects.create_user(
            email = 'test2@djangotest.com',
            username='testuser2',
            password='123456789'
        )

        self.client.login(username=secondaryUser.username, password='123456789')
        response = self.client.post(
            reverse('nulled_bill', kwargs={'account_id': self.account.id, 'bill_id': bill.id})
        )

        self.assertContains(response, '401 Unauthorized', status_code=401)

    def testWhenBillIsNulledThenAccountReplenishTheTotalOfSpend(self):
        self.client.login(username=self.user.username, password='123456789')
        fund = self.account.account_funds.first()
        fund.current_balance = 10000

        bill = Bill.objects.create(
            bill_number='00290012312',
            subtotal=Decimal(1400),
            iva=Decimal(100.00),
            total=Decimal(1500.00),
            pay_from_fund=fund
        )

        response = self.client.post(
            reverse('nulled_bill', kwargs={'account_id': self.account.id, 'bill_id': bill.id})
        )

        bill = Bill.objects.get(pk=bill.id)
        fund = AccountFunds.objects.get(pk=fund.id)
        movements = Movement.objects.all()

        self.assertIsNotNone(bill.bill_nulled_at)
        self.assertEqual(fund.current_balance, 10000)
        self.assertEqual(len(movements), 2)
        self.assertEqual(movements[1].funding, fund)
