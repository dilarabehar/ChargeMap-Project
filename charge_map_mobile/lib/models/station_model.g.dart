// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'station_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

EChargeStation _$EChargeStationFromJson(Map<String, dynamic> json) =>
    EChargeStation(
      stationName: json['stationName'] as String?,
      stationCode: json['stationCode'] as String?,
      stationCoordinate: json['stationCoordinate'] as String?,
      stationAddress: json['stationAddress'] as String?,
      stationTech: json['stationTech'] as String?,
      stationStatus: json['stationStatus'] as String?,
    );

Map<String, dynamic> _$EChargeStationToJson(EChargeStation instance) =>
    <String, dynamic>{
      'stationName': instance.stationName,
      'stationCode': instance.stationCode,
      'stationCoordinate': instance.stationCoordinate,
      'stationAddress': instance.stationAddress,
      'stationTech': instance.stationTech,
      'stationStatus': instance.stationStatus,
    };
