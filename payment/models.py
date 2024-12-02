from django.core import exceptions
from django.db import models
from django.contrib.auth.models import User
from productmanagement.models import Product
from sales.models import SalesPartner
from utils import keygen


class PaymentTracker(models.Model):
    key = models.CharField(max_length=200, unique=True, default='')

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = keygen.KeyGen().alphanumeric_key(200)
        super().save(*args, **kwargs)


class Purchase(models.Model):
    tracker = models.OneToOneField(PaymentTracker, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=200, unique=True, default='')
    key = models.CharField(max_length=200, default='')
    is_closed = models.BooleanField(default=False)
    issued_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __generate_transaction_id(self):
        return keygen.KeyGen().transaction_id()
    
    def update_transaction_id(self):
        self.transaction_id = self.__generate_transaction_id()
        self.save()
    
    def update_key(self, key:str):
        self.key = key
        self.save()
    
    @property
    def payable_amount(self):
        payable = self.product.price
        partner_bulk = SalesPartner.objects.filter(key=self.key)
        if partner_bulk.exists():
            partner = partner_bulk.first()
            payable = payable - partner.deductible_amount
        return payable if payable > 0 else 0
    
    def
        
    def close_transaction(self):
        if not self.is_closed:
            self.is_closed = True
            self.save()
        else: raise exceptions.ValidationError('Cannot close an already close transaction.')
    
    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = self.__generate_transaction_id()
        super().save(*args, **kwargs)
            
