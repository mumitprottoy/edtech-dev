from django.contrib import admin
from . import models

admin.site.register([
    models.Topic,
    models.Question,
    models.Option,
])