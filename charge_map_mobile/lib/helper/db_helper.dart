import 'dart:io';
import 'package:flutter/services.dart';
import 'package:path/path.dart';
import 'package:path_provider/path_provider.dart';
import 'package:sqflite/sqflite.dart';

import '../models/station_model.dart';

class DatabaseHelper {
  static final DatabaseHelper _instance = DatabaseHelper._internal();
  factory DatabaseHelper() => _instance;
  DatabaseHelper._internal();

  static Database? _database;

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDatabase();
    return _database!;
  }

  Future<List<String>> getTables() async {
    final db = await database;
    final tables = await db.rawQuery("SELECT name FROM sqlite_master WHERE type='table';");
    print('Tables in the database: $tables');
    return tables.map((row) => row['name'] as String).toList();
  }

  Future<Database> _initDatabase() async {
    final documentsDirectory = await getApplicationDocumentsDirectory();
    final path = join(documentsDirectory.path, 'e_charge_stations.db');
    final fileExists = await databaseExists(path);
    print('Database path: $path');
    print('Database exists: $fileExists');

    if (!fileExists) {
      print('Database does not exist. Copying from assets...');
      await _copyDatabaseFromAssets(path);
    } else {
      print('Database already exists.');
    }

    final db = await openDatabase(path);
    //await _createTableIfNotExists(db);
    return db;
  }

  Future<void> _copyDatabaseFromAssets(String path) async {
    try {
      final data = await rootBundle.load('assets/e_charge_stations.db');
      final bytes = data.buffer.asUint8List();
      await writeToFile(path, bytes);
      print('Database copied successfully to $path');
      await _inspectDatabase(path); // Inspect after copying
    } catch (e) {
      print('Error copying database from assets: $e');
    }
  }

  Future<void> _inspectDatabase(String path) async {
    try {
      final db = await openDatabase(path);
      final result = await db.rawQuery('SELECT name FROM sqlite_master WHERE type="table";');
      print('Tables in the database: $result');
    } catch (e) {
      print('Error inspecting database: $e');
    }
  }

  Future<void> _createTableIfNotExists(Database db) async {
    try {
      await db.execute('''
        CREATE TABLE IF NOT EXISTS e_charge_stations (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          station_name TEXT,
          station_code TEXT,
          station_coordinate TEXT,
          station_address TEXT,
          station_tech TEXT,
          station_status TEXT
        )
      ''');
      print("Table created or already exists.");
    } catch (e) {
      print('Error creating table: $e');
    }
  }

  Future<void> writeToFile(String path, List<int> bytes) async {
    try {
      final file = File(path);
      await file.writeAsBytes(bytes);
      print('Written to file: $path');
    } catch (e) {
      print('Error writing to file: $e');
    }
  }

  Future<List<Map<String, dynamic>>> query(String table) async {
    try {
      final db = await database;
      final result = await db.query(table);
      print('Query result for table $table: $result');
      return result;
    } catch (e) {
      print('Error querying table $table: $e');
      rethrow;
    }
  }

  Future<void> insertSampleData() async {
    try {
      final db = await database;
      await db.insert('e_charge_stations', {
        'station_name': 'Test Station',
        'station_code': 'TS001',
        'station_coordinate': '35.925533,32.866287',
        'station_address': 'Test Address',
        'station_tech': 'Test Tech',
        'station_status': 'Active'
      });
      print('Sample data inserted.');
    } catch (e) {
      print('Error inserting sample data: $e');
    }
  }

  Future<List<EChargeStation>> getAllStations() async {
    try {
      final db = await database;
      final List<Map<String, dynamic>> maps = await db.query('e_charge_stations');
      //print('Retrieved stations: $maps');

      return List.generate(maps.length, (i) {
        return EChargeStation(
          stationName: maps[i]['station_name'],
          stationCode: maps[i]['station_code'],
          stationCoordinate: maps[i]['station_coordinate'],
          stationAddress: maps[i]['station_address'],
          stationTech: maps[i]['station_tech'],
          stationStatus: maps[i]['station_status'],
        );
      });
    } catch (e) {
      print('Error retrieving all stations: $e');
      rethrow;
    }
  }
}
