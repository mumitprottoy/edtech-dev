from utils.images import urls
from .models import ProfilePictureURL, Name
from utils.words import words

def create():
    for url in urls:
        ProfilePictureURL(url=url).save()

def add_names():
    for word in words:
        Name(word=word).save()
