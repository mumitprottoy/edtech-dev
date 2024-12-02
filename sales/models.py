from django.db import models
from django.contrib.auth.models import User


class SalesPartner(models.Model):
    ADV = 'Learning Advocate'; GUIDE = 'Learning Guide'; REF = 'Referrer'
    PARTNER_TYPE_CHOICES = ((ADV, ADV), (GUIDE, GUIDE), (REF, REF))
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='partner')
    partner_type = models.CharField(max_length=20, choices=PARTNER_TYPE_CHOICES)
    coupon_code = models.CharField(max_length=20, unique=True)    
    link = models.CharField(max_length=200, unique=True)
    deductible_amount = models.IntegerField(default=0)
    
    def __str__(self) -> str:
        return f'{self.user.email} : {self.partner_type}'    
