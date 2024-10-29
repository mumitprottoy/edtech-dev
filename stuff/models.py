import random
from django.db import models


class ProfilePictureURL(models.Model):
    url = models.TextField()
    
    class Meta:
        verbose_name_plural = 'Profile Picture URLs'


class Logo(models.Model):
    name = models.CharField(
        max_length=10, unique=True, default='Main')
    url = models.TextField()
    
    def __str__(self) -> str:
        return self.name


class MainCopy(models.Model):
    title = models.CharField(max_length=500)
    copy = models.TextField()
    url = models.TextField()
    
    class Meta:
        verbose_name_plural = 'Main Copies'
    
    def __str__(self) -> str:
        return self.title


class PrimaryImageCopy(models.Model):
    url = models.TextField()


class Name(models.Model):
    word = models.CharField(max_length=20, unique=True)
    
    @classmethod
    def get_random_name(cls) -> list:
        full_name = list()
        name_list = list(cls.objects.all())
        for _ in range(2):
            index = random.choice(len(name_list))
            full_name.append(name_list[index])
            name_list.pop(index)
        return full_name

    def __str__(self) -> str:
        return self.word