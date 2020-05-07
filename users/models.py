from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()
