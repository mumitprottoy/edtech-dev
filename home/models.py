from django.db import models
from django.core import exceptions


class C(models.Model):
    x = models.IntegerField(default=-1)
    
    def save(self, *args, **kwargs):
        self.x += 1
        if self.x > 1:
            raise exceptions.ValidationError('Already attempted.')
        super().save(*args, **kwargs)
