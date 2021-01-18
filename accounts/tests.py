from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.test import TestCase, Client

from .models import AccountEntityType, Account, AccountEntityFinancial


# Create your tests here.

class EntityFinancialModelTest(TestCase):
    def setUp(self):
        type = AccountEntityType.objects.create(
            entity_type='BN'
        )

        AccountEntityFinancial.objects.create(
            type=type,
            entity_name='Banco de Venezuela',
            entity_name_abbr='BDV',
            entity_prefix_account='0102'
        )

    def testTypeIsInstanceOfAccountEntityTypeModel(self):
        entity = AccountEntityFinancial.objects.get(pk=1)
        type = AccountEntityType.objects.get(pk=1)

        self.assertIsInstance(entity.type, AccountEntityType)
        self.assertEqual(entity.type, type)


class AccountModelTest(TestCase):

    def setUp(self):
        user = User.objects.create(
            first_name='Test user',
            email='algo@mail.com',
            password='1234521'
        )

        type = AccountEntityType.objects.create(
            entity_type='BN'
        )
        entity = AccountEntityFinancial.objects.create(
            type=type,
            entity_name='Banco de Venezuela',
            entity_name_abbr='BDV',
            entity_prefix_account='0102'
        )
        Account.objects.create(
            owner=user,
            entity=entity,
            account_code='EXAMPLE CODE',
            account_type='C'
        )

    def testAccountOwnerIsUserModelInstance(self):
        user = User.objects.get(pk=1)
        account = Account.objects.get(pk=1)
        self.assertEqual(account.account_code, 'EXAMPLE CODE')
        self.assertIsInstance(account.owner, User)
        self.assertEqual(account.owner, user)

    def testAccountTypeIsInstanceOfAccountEntityFinancialModel(self):
        account = Account.objects.get(pk=1)

        self.assertIsInstance(account.entity, AccountEntityFinancial)
        self.assertNotIsInstance(account.entity, QuerySet)

    def testGetByUserMethodFromManager(self):
        user = User.objects.get(pk=1)
        accounts = Account.objects.getByUser(user)

        self.assertIsNotNone(accounts)
        self.assertIsInstance(accounts, QuerySet)
        self.assertGreater(len(accounts), 0)

    def testGetByUserFromManagerWhenUserNotHasAccounts(self):
        User.objects.create(
            username='Usertest_2',
            email='usertest@gmail.2com',
            password='12345123'
        )

        user = User.objects.filter(username='Usertest_2')[0]
        accounts = Account.objects.getByUser(user)

        self.assertEqual(len(accounts), 0)

    def testGetByUserFromManagerWhenUserParamIsNumeric(self):
        accounts = Account.objects.getByUser(1)
        accountUser2 = Account.objects.getByUser(3)

        self.assertEqual(len(accounts), 1)
        self.assertEqual(accounts[0].account_code, 'EXAMPLE CODE')

        self.assertEqual(len(accountUser2), 0)


class HttpCrudAccountTest(TestCase):

    def setUp(self):
        self.client = Client()
        User.objects.create_user(
            username='gjavilae',
            email='gjavilae@gmail.com',
            password='123456789'
        )
        self.type = AccountEntityType.objects.create(
            entity_type='BN'
        )
        self.entity = AccountEntityFinancial.objects.create(
            type=self.type,
            entity_name='BANCO DE VENEZUELA',
            entity_name_abbr='BDV',
            entity_prefix_account='0102'
        )

    def testCreateANewBankAccount(self):
        self.client.login(username='gjavilae', password='123456789')

        resp = self.client.post('/dashboard/cuentas/create/', {
            'entity': 1,
            'account_code': '000000000',
            'account_type': 'C'
        })

        account = Account.objects.first()

        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, '/dashboard/cuentas/?success=True')
        self.assertIsNotNone(account)
        self.assertEqual(account.owner, User.objects.first())
        self.assertEqual(account.account_code, '000000000')

    def testPostToDeleteAccount(self):
        user = User.objects.first()
        self.client.login(username='gjavilae', password='123456789')
        acc = Account.objects.create(
            entity=self.entity,
            account_code='00000000',
            account_type='C',
            owner=user
        )

        resp = self.client.post(f'/dashboard/cuentas/{acc.id}/delete')
        accs = Account.objects.getByUser(user)

        self.assertRedirects(resp, '/dashboard/cuentas/?success=True')
        self.assertEqual(len(accs), 0)


    def testDisplayOnlyUserAccountsOnListView(self):
        user = User.objects.create_user(username='user2', email='user2@gmail.com', password='123456789')
        Account.objects.create(
            entity=self.entity,
            account_code='00000001',
            account_type='C',
            owner=user
        )
        Account.objects.create(
            entity=self.entity,
            account_code='00000002',
            account_type='C',
            owner=user
        )

        Account.objects.create(
            entity=self.entity,
            account_code='00000032',
            account_type='C',
            owner=User.objects.filter(username='gjavilae')[0]
        )

        self.client.login(username='gjavilae', password='123456789')

        resp = self.client.get('/dashboard/cuentas/')

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'accounts.html')
        self.assertNotContains(resp, '010200000002')
        self.assertContains(resp, '010200000032')