from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    is_worker = models.BooleanField(default=False)
    is_staff_member = models.BooleanField(default=False)

    def __str__(self):
        return self.username