from decimal import Decimal
from django.test import TestCase

from django.contrib.auth.models import User
from accounts.models import Account, AccountEntityType, AccountEntityFinancial
from movements.models import AccountFunds, Movement
from .models import Bill


class TestBillModel(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@gmail.com',
            username='testuser',
            password='12345123'
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
        self.assertGreater(len(movements), 0)

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