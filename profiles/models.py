import random
from django.db import models
from django.contrib.auth.models import User
from stuff import models as stuff_models


class Picture(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='pic')
    url = models.TextField(default='')
    
    def choose_pic(self) -> stuff_models.ProfilePictureURL:
        urls = list(stuff_models.ProfilePictureURL.objects.all())
        return random.choice(urls)
    
    def save(self, *args, **kwargs):
        if not self.url:
            self.url = self.choose_pic().url
        super().save(*args, **kwargs)


class Phone(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='phone')
    number = models.CharField(max_length=20, default='') 
    
        
class UserStatus(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='status')
    is_premium = models.BooleanField(default=False)
    
    