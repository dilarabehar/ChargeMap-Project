from django.urls import path
from . import views
from .views import MapView, GeoCodingView, SearchView, DistanceView, RouteView

urlpatterns = [
    path('home/', views.home, name='home'),
    path('map/', MapView.as_view(), name='my_map_view'),
    path('station/<int:pk>/', GeoCodingView.as_view(), name='geocoding_view'),
    path('search/<int:pk>', SearchView.as_view(), name='search'),
    path('distance/', DistanceView.as_view(), name='distance'),
    path('route/', RouteView.as_view(), name='route'),
]
