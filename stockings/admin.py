# stockings/admin.py

from django.contrib import admin
from .models import BodyOfWater, FishStocking

@admin.register(BodyOfWater)
class BodyOfWaterAdmin(admin.ModelAdmin):
    list_display = ('name', 'latitude', 'longitude')
    search_fields = ('name',)

@admin.register(FishStocking)
class FishStockingAdmin(admin.ModelAdmin):
    list_display = ('body_of_water', 'stocking_date', 'species', 'quantity')
    search_fields = ('body_of_water__name', 'species')
    list_filter = ('stocking_date',)
