from django.contrib import admin
from .models import EChargeStations

@admin.register(EChargeStations)
class EChargeStationsAdmin(admin.ModelAdmin):
    list_display = ('station_name', 'station_code', 'station_address')


