from django.db.models import manager, Model

class AccountManager(manager.Manager):

    def getByUser(self, user):
        userQueryset = []

        if isinstance(user, Model):
            userQueryset = self.filter(owner=user)
        elif isinstance(user, int):
            userQueryset = self.filter(owner__id=user)

        return userQueryset
