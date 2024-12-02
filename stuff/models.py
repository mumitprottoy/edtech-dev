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
    ADJ = 'adjectives'; NOUN = 'nouns'
    POS_CHOICES = ((ADJ, ADJ), (NOUN, NOUN))
    pos = models.CharField(choices=POS_CHOICES, max_length=10)
    word = models.CharField(max_length=20, unique=True)
    
    @classmethod
    def get_random_name(cls) -> list:
        first_name = random.choice(list(cls.objects.filter(pos=cls.ADJ))).word
        last_name = random.choice(list(cls.objects.filter(pos=cls.NOUN))).word
        return first_name, last_name
    
    @classmethod
    def fetch_words(cls):
        cls.objects.all().delete()
        import requests
        resolve_url = lambda pos: f'https://www.randomlists.com/data/{pos}.json'
        for pos in ('adjectives', 'nouns'):
            words = requests.get(url=resolve_url(pos)).json()['data']
            for word in words:
                if not cls.objects.filter(word=word.capitalize()).exists():
                    cls(pos=pos, word=word.capitalize()).save()

    def __str__(self) -> str:
        return self.word
    
    
class Image(models.Model):
    name = models.CharField(max_length=20, unique=True)
    url = models.TextField()
    
    def __str__(self):
        return self.name