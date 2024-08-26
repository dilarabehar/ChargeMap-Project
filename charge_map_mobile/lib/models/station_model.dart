import 'package:json_annotation/json_annotation.dart';

part 'station_model.g.dart'; // Bu dosya build_runner tarafından oluşturulacak

@JsonSerializable()
class EChargeStation {
  final String? stationName;
  final String? stationCode;
  final String? stationCoordinate;
  final String? stationAddress;
  final String? stationTech;
  final String? stationStatus;

  EChargeStation({
    this.stationName,
    this.stationCode,
    this.stationCoordinate,
    this.stationAddress,
    this.stationTech,
    this.stationStatus,
  });

  factory EChargeStation.fromJson(Map<String, dynamic> json) => _$EChargeStationFromJson(json);
  Map<String, dynamic> toJson() => _$EChargeStationToJson(this);
}
