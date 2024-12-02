from django.contrib import admin
from . import models

admin.site.register([
    models.Logo, 
    models.MainCopy, 
    models.PrimaryImageCopy,
    models.ProfilePictureURL,
    models.Name,
    models.Image
])

