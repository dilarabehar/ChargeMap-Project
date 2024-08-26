import 'dart:async';
import 'package:flutter_polyline_points/flutter_polyline_points.dart';
import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:location/location.dart';
import 'package:permission_handler/permission_handler.dart';
import '../helper/db_helper.dart';
import '../models/station_model.dart';
import 'package:location/location.dart' as location;
import 'package:permission_handler/permission_handler.dart' as permission_handler;
import 'package:charge_map_mobile/consts.dart';

class MapPage extends StatefulWidget {
  const MapPage({super.key});

  @override
  State<MapPage> createState() => _MapPageState();
}

class _MapPageState extends State<MapPage> {
  Location _locationController = Location();
  LatLng? _currentPostion;
  final Completer<GoogleMapController> _mapController = Completer<GoogleMapController>();
  Map<PolylineId, Polyline> polyLines = {};
  Set<Marker> _markers = {};
  static const LatLng _pGooglePlex = LatLng(35.925533, 32.866287);
  late Future<List<EChargeStation>> _stations;

  @override
  void initState() {
    super.initState();
    _requestPermissions();
    _stations = DatabaseHelper().getAllStations();
    getLocationUpdate();
  }

  Future<void> _requestPermissions() async {
    await [
      Permission.location,
      Permission.locationWhenInUse,
    ].request();
  }

  LatLng parseDMSCoordinate(String dms) {
    final parts = dms.split(' ');
    if (parts.length < 9) return LatLng(0.0, 0.0); // Invalid format check

    // Latitude components
    final latDegrees = _parseCoordinate(parts[0]);
    final latMinutes = _parseCoordinate(parts[1]);
    final latSeconds = _parseCoordinate(parts[2]);
    final latDirection = parts[3];

    // Longitude components
    final lonDegrees = _parseCoordinate(parts[5]);
    final lonMinutes = _parseCoordinate(parts[6]);
    final lonSeconds = _parseCoordinate(parts[7]);
    final lonDirection = parts[8];

    // Convert latitude and longitude to decimal degrees
    double latitude = latDegrees + latMinutes / 60 + latSeconds / 3600;
    double longitude = lonDegrees + lonMinutes / 60 + lonSeconds / 3600;

    // Adjust based on direction
    if (latDirection == 'S') latitude = -latitude;
    if (lonDirection == 'W') longitude = -longitude;

    return LatLng(latitude, longitude);
  }

  double _parseCoordinate(String coordinatePart) {
    final number = double.tryParse(coordinatePart.replaceAll(RegExp(r'[^\d.]'), ''));
    return number ?? 0.0;
  }

  Set<Marker> _createMarkers(List<EChargeStation> stations) {
    final markers = <Marker>{};
    for (var station in stations) {
      final latLng = parseDMSCoordinate(station.stationCoordinate ?? '');
      markers.add(
        Marker(
          markerId: MarkerId(station.stationCode ?? ''),
          position: latLng,
          icon: BitmapDescriptor.defaultMarker,
          infoWindow: InfoWindow(
            title: station.stationName,
            snippet: station.stationAddress,
          ),
          onTap: () {
            _onMarkerTapped(station.stationCode ?? '', latLng);
          },
        ),
      );
      if (_currentPostion != null) {
        markers.add(
          Marker(
            markerId: MarkerId('current_location'),
            position: _currentPostion!,
            icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueBlue),
            infoWindow: InfoWindow(
              title: 'Current Location',
            ),
          ),
        );
      }
    }
    return markers;
  }

  void _onMarkerTapped(String stationCode, LatLng markerPosition) async {
    if (_currentPostion != null) {
      final polylineCoordinates = await getPolylinePosition(_currentPostion!, markerPosition);
      generatePolyLineFromPoints(polylineCoordinates);
      _cameraToPosition(markerPosition);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: FutureBuilder<List<EChargeStation>>(
        future: _stations,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          } else if (!snapshot.hasData || snapshot.data!.isEmpty) {
            return Center(child: Text('No data available'));
          } else {
            final markers = _createMarkers(snapshot.data!);
            return GoogleMap(
              onMapCreated: (GoogleMapController controller) => _mapController.complete(controller),
              initialCameraPosition: CameraPosition(
                target: _currentPostion ?? _pGooglePlex,
                zoom: 5,
              ),
              markers: markers,
              polylines: Set<Polyline>.of(polyLines.values),
            );
          }
        },
      ),
    );
  }

  Future<void> _cameraToPosition(LatLng pos) async {
    final GoogleMapController controller = await _mapController.future;
    CameraPosition _newCameraPosition = CameraPosition(target: pos, zoom: 16);
    await controller.animateCamera(CameraUpdate.newCameraPosition(_newCameraPosition));
  }

  Future<void> getLocationUpdate() async {
    bool _serviceEnabled;
    location.PermissionStatus _permissionGranted;

    _serviceEnabled = await _locationController.serviceEnabled();
    if (!_serviceEnabled) {
      _serviceEnabled = await _locationController.requestService();
      if (!_serviceEnabled) {
        return;
      }
    }

    _permissionGranted = await _locationController.hasPermission();
    if (_permissionGranted == location.PermissionStatus.denied) {
      _permissionGranted = await _locationController.requestPermission();
      if (_permissionGranted != location.PermissionStatus.granted) {
        return;
      }
    }

    _locationController.onLocationChanged.listen((LocationData currentLocation) {
      if (currentLocation.latitude != null && currentLocation.longitude != null) {
        setState(() {
          _currentPostion = LatLng(currentLocation.latitude!, currentLocation.longitude!);
          print("Current Position: $_currentPostion");
          _cameraToPosition(_currentPostion!);
        });
      }
    });
  }

  Future<List<LatLng>> getPolylinePosition(LatLng currentPosition, LatLng destination) async {
    List<LatLng> polylineCoordinates = [];
    PolylinePoints polylinePoints = PolylinePoints();
    PolylineResult result = await polylinePoints.getRouteBetweenCoordinates(
      googleApiKey: GOOGLE_MAPS_API_KEY,
      request: PolylineRequest(
        origin: PointLatLng(currentPosition.latitude, currentPosition.longitude),
        destination: PointLatLng(destination.latitude, destination.longitude),
        mode: TravelMode.driving,
      ),
    );
    if (result.points.isNotEmpty) {
      result.points.forEach((PointLatLng point) {
        polylineCoordinates.add(LatLng(point.latitude, point.longitude));
      });
    } else {
      print(result.errorMessage);
    }
    return polylineCoordinates;
  }

  void generatePolyLineFromPoints(List<LatLng> polylineCoordinates) {
    PolylineId id = PolylineId("poly");
    Polyline polyline = Polyline(
      polylineId: id,
      color: Colors.lightBlueAccent,
      points: polylineCoordinates,
      width: 8,
    );
    setState(() {
      polyLines[id] = polyline;
    });
  }
}
