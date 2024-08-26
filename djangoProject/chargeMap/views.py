import googlemaps
from django.shortcuts import render, redirect
from django.views import View

from djangoProject2 import settings
from .models import EChargeStations

import requests
import folium
from .forms import *
from datetime import datetime

import re


def index(request):
    return render(request, 'index.html')


def home(request):
    stations = EChargeStations.objects.all()
    return render(request, 'home.html', {'stations': stations})


class GeoCodingView(View):
    template_name = 'geocoding.html'

    def get(self, request, pk):
        key = settings.GOOGLE_API_KEY
        chosen_station = EChargeStations.objects.get(pk=pk)
        context = {
            "chosen_station": chosen_station,
        }
        return render(request, self.template_name, context)


class SearchView(View):
    template_name = 'index.html'

    def get(self, request, pk):
        key = settings.GOOGLE_API_KEY
        res = requests.get('https://ipinfo.io/')
        ip = res.json()
        local_ip = ip['loc'].split(',')
        lat = local_ip[0]
        lon = local_ip[1]
        chosen_station = EChargeStations.objects.get(pk=pk)
        coordinate = chosen_station.station_coordinate
        latitude, longitude = parse_dms(coordinate)
        marked_station = []
        data = {
            'lat': float(latitude),
            'lng': float(longitude),
            'name': chosen_station.station_name,
            'address': chosen_station.station_address,
            'tech': chosen_station.station_tech,
            'status': chosen_station.station_status,
            'code': chosen_station.station_code,
        }
        marked_station.append(data)
        context = {
            "key": key,
            "lat": lat,
            "lon": lon,
            "chosen_station": chosen_station,
            "marked_station": marked_station,
        }

        return render(request, self.template_name, context)


class MapView(View):
    template_name = 'map.html'

    def get(self, request):
        key = settings.GOOGLE_API_KEY
        eligable_locations = EChargeStations.objects.filter(station_coordinate__isnull=False)
        #coordinates = EChargeStations.objects.values("station_coordinate")
        locations = []

        for a in eligable_locations:
            coordinates = a.station_coordinate
            latitude, longitude = parse_dms(coordinates)

            data = {
                'lat': float(latitude),
                'lng': float(longitude),
                'name': a.station_name,
                'address': a.station_address,
                'tech': a.station_tech,
                'status': a.station_status,
                'code': a.station_code,
            }
            locations.append(data)

        context = {
            "key": key,
            "locations": locations,
        }
        return render(request, self.template_name, context)


class DistanceView(View):
    template_name = 'distance.html'

    def get(self, request):
        key = settings.GOOGLE_API_KEY
        form = DistanceForm
        distances = Distance.objects.all()
        context = {
            "form": form,
            "distances": distances,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = DistanceForm(request.POST)
        if form.is_valid():
            from_location = form.cleaned_data['from_location']
            from_location_info = EChargeStations.objects.get(station_code=from_location)
            from_address_string = str(from_location_info.station_address) + " " + (
                from_location_info.station_coordinate)

            to_location = form.cleaned_data['to_location']
            to_location_info = EChargeStations.objects.get(station_code=to_location)
            to_address_string = str(to_location_info.station_address) + " " + (to_location_info.station_coordinate)

            mode = form.cleaned_data['mode']
            now = datetime.now()
            gmaps = googlemaps.Client(key=settings.GOOGLE_API_KEY)
            calculate = gmaps.distance_matrix(
                from_address_string,
                to_address_string,
                mode=mode,
                departure_time=now,
            )

#calculate
#{'destination_addresses': ['Haydarpaşa, Rasimpaşa, 34716 Kadıköy/İstanbul, '
#                           'Türkiye'],
# 'origin_addresses': ['Hacımercan, 54600 Sapanca/Sakarya, Türkiye'],
#'rows': [{'elements': [{'distance': {'text': '130 km', 'value': 130224},
#                        'duration': {'text': '1 day 6 hours', 'value': 107084},
#                       'status': 'OK'}]}],
#'status': 'OK'}

            if calculate['status'] == 'OK':
                distance = calculate['rows'][0]['elements'][0]['distance']['text']
                duration = calculate['rows'][0]['elements'][0]['duration']['text']

                print(f"From: {str(from_location)}, To: {str(to_location)}")
                print(f"Distance: {distance}")
                print(f"Duration: {duration}")


                obj = Distance(
                    from_location=EChargeStations.objects.get(station_code=from_location),
                    to_location=EChargeStations.objects.get(station_code=to_location),
                    mode=mode,
                    distance_km=distance,
                    duration_mins=duration
                )
                #obj.save()
                context = {
                    'distance': distance,
                    'duration': duration,
                    'form': form,
                }
                return render(request, 'distance.html', context)
            else:
                print("Error in API response.")
                return render(request, 'distance.html', {'form': form, 'error': 'Error in API response.'})

        else:
            print("invalid")

        return redirect('distance')

class RouteView(View):
    template_name = 'route.html'
    def get(self, request):
        key = settings.GOOGLE_API_KEY
        form = DistanceForm
        distances = Distance.objects.all()
        context = {
            "form": form,
            "distances": distances,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = DistanceForm(request.POST)
        if form.is_valid():
            from_location = form.cleaned_data['from_location']
            from_location_info = EChargeStations.objects.get(station_code=from_location)
            from_address_string = str(from_location_info.station_address) + " " + (
                from_location_info.station_coordinate)

            to_location = form.cleaned_data['to_location']
            to_location_info = EChargeStations.objects.get(station_code=to_location)
            to_address_string = str(to_location_info.station_address) + " " + (to_location_info.station_coordinate)

            mode = form.cleaned_data['mode']
            gmaps = googlemaps.Client(key=settings.GOOGLE_API_KEY)
            calculate = gmaps.DirectionsService(
                to_address_string,
                from_address_string,
            )

            context = {
                "form": form,
            }
            return render(request, 'distance.html', context)
        else:
            print("Error in API response.")



def dms_to_decimal(degree, minute, second, direction):
    """DMS formatını ondalıklı dereceye dönüştürür."""
    decimal = float(degree) + float(minute) / 60 + float(second) / (60 * 60)
    if direction in ['S', 'W']:
        decimal = -decimal
    return decimal


def parse_dms(dms_str):
    """DMS formatındaki bir koordinat stringini ayrıştırır ve ondalıklı dereceye dönüştürür."""
    # Regex ile derece, dakika, saniye ve yön bilgilerini ayıkla
    regex = r"(\d+)° (\d+)' (\d+\.?\d*)\" ([NS])\s+(\d+)° (\d+)' (\d+\.?\d*)\" ([EW])"
    match = re.match(regex, dms_str)
    if match:
        lat_deg, lat_min, lat_sec, lat_dir, lon_deg, lon_min, lon_sec, lon_dir = match.groups()

        latitude = dms_to_decimal(lat_deg, lat_min, lat_sec, lat_dir)
        longitude = dms_to_decimal(lon_deg, lon_min, lon_sec, lon_dir)

        return latitude, longitude
    else:
        raise ValueError(f"Geçersiz DMS formatı: {dms_str}")
