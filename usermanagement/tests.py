from django.test import TestCase, Client
from django.contrib.auth.models import User


# Create your tests here.
class LoginTest(TestCase):

    def setUp(self):
        User.objects.create_user(username='gjavilae', email='gjavilae@gmail.com', password='123456789')

    def testWhenUserIsNotLoggedThenCantViewDashboardPage(self):
        c = Client()
        resp = c.get('/dashboard/')

        self.assertRedirects(resp, '/login?login_url=/dashboard/', target_status_code=301)

    def testWhenUserHasBeenLogin(self):
        self.client.login(username='gjavilae', password='123456789')

        resp = self.client.get('/dashboard/')
        self.assertEqual(resp.status_code, 200)
