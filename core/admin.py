from django.contrib import admin
from . import models

admin.site.register(models.User)
admin.site.register(models.Stock)
admin.site.register(models.News)
admin.site.register(models.Transaction)
admin.site.register(models.Portfolio)
admin.site.register(models.Holding)