from django.contrib import admin
from .models import Sector, Stock, UserProfile, NiftyData, StockData

# Register your models here.
admin.site.register(Sector)
admin.site.register(Stock)
admin.site.register(UserProfile)
admin.site.register(NiftyData)
admin.site.register(StockData)
