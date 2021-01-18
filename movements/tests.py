from django.db.models.signals import post_save
from django.dispatch import receiver
from django.test import TestCase, Client
from django.contrib.auth.models import User
from unittest.mock import patch

from accounts.models import Account, AccountEntityType, AccountEntityFinancial
from .models import AccountFunds, Movement
from .exceptions import AccountFundArgumentError
from .signals import create_account_default_fund


# Create your tests here.
class BaseModuleTest(TestCase):

    def setUp(self, *args, **kwargs):
        # post_save.disconnect(create_account_default_fund, sender=Account)
        self.user = User.objects.create_user(username='gjavilae', password='123456789', email='gjavilae')
        self.type_account = AccountEntityType.objects.create(entity_type='BN')
        self.entity = AccountEntityFinancial.objects.create(
            type=self.type_account,
            entity_name='Banco de venezuela',
            entity_name_abbr='BDV',
            entity_prefix_account='0102'
        )
        self.account = Account.objects.create(
            owner=self.user,
            entity=self.entity,
            account_code='012342124512',
            account_type='C'
        )


class AccountFundModelTest(BaseModuleTest):

    def testEnvironmentSetup(self, *args, **kwargs):
        accounts = Account.objects.all()
        funds = AccountFunds.objects.all()

        self.assertIsNotNone(self.user)
        self.assertEqual(len(accounts), 1)

    def testAccountHasFund(self, *args, **kw):
        fund = AccountFunds.objects.create(account=self.account)
        funds = AccountFunds.objects.all()

        self.assertEqual(len(funds), 2)
        self.assertIsInstance(fund.account, Account)

    def testAccountFundAddToBalance(self):
        fund = AccountFunds.objects.create(account=self.account, current_balance=1000)
        fund.addToBalance(1500)

        currentFund = AccountFunds.objects.get(pk=fund.id)

        self.assertEqual(currentFund.current_balance, 2500)
        self.assertEqual(currentFund.input_balance, 1500)

    def testAccountFundSubToBalance(self):
        fund = AccountFunds.objects.create(account=self.account, current_balance=1000)
        fund.subToBalance(300)

        currentFund = AccountFunds.objects.get(pk=fund.id)

        self.assertEqual(currentFund.current_balance, 700)
        self.assertEqual(currentFund.output_balance, 300)
        self.assertEqual(currentFund.input_balance, 0)


class CreateAccountAndDefaultFund(BaseModuleTest):

    def setUp(self):
        super().setUp()
        self.client = Client()
        self.client.login(username='gjavilae', password='123456789')

    def testRequestCreateAccount(self):
        resp = self.client.post('/dashboard/cuentas/create', {
            'entity': self.entity.id,
            'account_code': '00000000',
            'accoubt_type': 'C'
        })
        accs = Account.objects.all()
        funds = AccountFunds.objects.all()

        self.assertEqual(301, resp.status_code)
        # self.assertRedirects(resp, '/dashboard/cuentas/?success=True', status_code=301)
        self.assertEqual(len(accs), 1)
        self.assertEqual(len(funds), 1)


class MovementModelTest(BaseModuleTest):

    def testMovementCreatedExceptionOnFundTypes(self):
        with self.assertRaises(AccountFundArgumentError) as ErrorExpected:
            Movement.create_movement(None, None, 1500.0)

    def testCreateMovementToAccount(self):
        fund = AccountFunds.objects.create(account=self.account, current_balance=1000)
        from_fund = AccountFunds.objects.create(account=self.account, current_balance=7000)

        Movement.create_movement(
            from_fund=from_fund,
            to_fund=fund,
            amount=1500,
            subject="Transferencia para panas"
        )

        fund = AccountFunds.objects.get(pk=fund.id)
        from_fund = AccountFunds.objects.get(pk=from_fund.id)
        movement = Movement.objects.last()

        self.assertEqual(fund.current_balance, 2500)
        self.assertEqual(fund.input_balance, 1500)
        self.assertEqual(from_fund.current_balance, 5500)
        self.assertEqual(from_fund.output_balance, 1500)
        self.assertIsNotNone(movement.transaction_id)

    def testWhenAccountSenderNoHasEnoughFunds(self):
        fund = AccountFunds.objects.create(account=self.account, current_balance=1000)
        from_fund = AccountFunds.objects.create(account=self.account, current_balance=1400)

        with self.assertRaises(ValueError) as ExceptionExpected:
            Movement.create_movement(from_fund, fund, 2400)

        fundReceiver = AccountFunds.objects.get(pk=fund.id)
        self.assertEqual(fund.current_balance, fundReceiver.current_balance)

    def testGetAllMovementsByUser(self):
        fund = AccountFunds.objects.create(account=self.account, current_balance=1000)
        from_fund = AccountFunds.objects.create(account=self.account, current_balance=10000)
        Movement.objects.create(
            amount=100,
            funding=fund,
            from_account_funds=from_fund
        )
        Movement.objects.create(
            amount=100,
            funding=fund,
            from_account_funds=from_fund
        )
        Movement.objects.create(
            amount=100,
            funding=fund,
            from_account_funds=from_fund
        )

        allByUser = Movement.objects.movementsByUser(self.user)
        self.assertEqual(len(allByUser), 3)
        self.assertEqual(allByUser[0].movement_type, Movement.RECEIVED_DESCRIPTION)

    def testGetOnlyMovementTypeSenders(self):
        newUser = User.objects.create_user(
            username='testuser2',
            password='123456789',
            email='testmail@gmail.com'
        )
        account2 = Account.objects.create(
            owner=newUser,
            entity=self.entity,
            account_code='012342124513',
            account_type='C'
        )

        fund = AccountFunds.objects.create(account=self.account, current_balance=1000)
        from_fund = AccountFunds.objects.create(account=account2, current_balance=10000)
        send = Movement.objects.create(
            amount=100,
            funding=from_fund,
            from_account_funds=fund
        )
        Movement.objects.create(
            amount=100,
            funding=fund,
            from_account_funds=from_fund
        )
        Movement.objects.create(
            amount=100,
            funding=fund,
            from_account_funds=from_fund
        )

        sendMovements = Movement.objects.getOnlySenderByUser(self.user)

        self.assertEqual(len(sendMovements), 1)
        self.assertEqual(sendMovements[0], send)

    def testGetOnlyReceiveds(self):
        newUser = User.objects.create_user(
            username='testuser2',
            password='123456789',
            email='testmail@gmail.com'
        )
        account2 = Account.objects.create(
            owner=newUser,
            entity=self.entity,
            account_code='012342124513',
            account_type='C'
        )

        fund = AccountFunds.objects.create(account=self.account, current_balance=1000)
        from_fund = AccountFunds.objects.create(account=account2, current_balance=10000)
        Movement.objects.create(
            amount=100,
            funding=from_fund,
            from_account_funds=fund
        )
        Movement.objects.create(
            amount=100,
            funding=fund,
            from_account_funds=from_fund
        )
        Movement.objects.create(
            amount=100,
            funding=fund,
            from_account_funds=from_fund
        )

        receivedMovements = Movement.objects.getOnlyReceivedsByUser(self.user)
        allMovements = Movement.objects.all()

        self.assertEqual(len(receivedMovements), 2)
        self.assertEqual(len(allMovements), 3)

    def testGetAllMovementsByAccount(self):
        newUser = User.objects.create_user(
            username='testuser2',
            password='123456789',
            email='testmail@gmail.com'
        )
        account2 = Account.objects.create(
            owner=newUser,
            entity=self.entity,
            account_code='012342124513',
            account_type='C'
        )

        fund = AccountFunds.objects.create(account=self.account, current_balance=1000)
        from_fund = AccountFunds.objects.create(account=account2, current_balance=10000)
        Movement.objects.create(
            amount=100,
            funding=from_fund,
            from_account_funds=fund
        )
        Movement.objects.create(
            amount=100,
            funding=fund,
            from_account_funds=from_fund
        )
        Movement.objects.create(
            amount=100,
            funding=fund,
            from_account_funds=from_fund
        )

        allByAccount = Movement.objects.getMovementsByAccount(account2)
        self.assertEqual(len(allByAccount), 3)
        self.assertIsNotNone(allByAccount[0].movement_type)
        self.assertEqual(allByAccount[0].movement_type, Movement.RECEIVED_DESCRIPTION)
        self.assertEqual(allByAccount[2].movement_type, Movement.SEND_DESCRIPTION)