# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

class Distance(models.Model):
    from_location = models.ForeignKey('EChargeStations', models.DO_NOTHING, db_column='from_location', blank=True, null=True)
    to_location = models.ForeignKey('EChargeStations', models.DO_NOTHING, db_column='to_location', related_name='distance_to_location_set', blank=True, null=True)
    mode = models.TextField(blank=True, null=True)
    distance_km = models.TextField(blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    duration_mins = models.TextField(blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    duration_traffic_mins = models.TextField(blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'distance'

    def __str__(self):
        return self.id


class EChargeStations(models.Model):
    station_name = models.TextField(blank=True, null=True)
    station_code = models.TextField(blank=True, null=True)
    station_coordinate = models.TextField(blank=True, null=True)
    station_address = models.TextField(blank=True, null=True)
    station_tech = models.TextField(blank=True, null=True)
    station_status = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'e_charge_stations'

    def __str__(self):
        return self.station_code

