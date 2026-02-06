#include <Arduino.h>
#include <ArduinoJson.h> // Ensure you are using ArduinoJson v7.x

// --- CONFIGURATION ---
const long BAUD_RATE = 9600;

// Simulation Variables (Replace these with your real sensor logic later)
double simLat = 7.0;
double simLon = 80.0;
float simAlt = 0.0;
float simTemp = 25.0;

float simaX = 0.12, simaY = 0.05, simaZ = 9.81;
float simgX = 0.01, simgY = 0.00, simgZ = -0.01;
float simmX = 15.0, simmY = 22.5, simmZ = 40.2;

float simRssi = -70.5;
float simSnr = 7.3;

void setup() {
  Serial.begin(BAUD_RATE);
  // Wait a moment for Serial to stabilize
  delay(1000);
}

// Function to package data and send to Serial (and CSV via Python)
void sendTelemetry(uint32_t timestamp, float temp, double lat, double lon, float alt, 
                   float ax, float ay, float az, 
                   float gx, float gy, float gz, 
                   float mx, float my, float mz, float rssi, float snr) {
                   
  // FIX: In ArduinoJson v7, use JsonDocument instead of StaticJsonDocument<SIZE>
  // The library now manages memory elastically (like a std::string).
  JsonDocument doc;

  // Populate the JSON object
  doc["timestamp"] = timestamp;
  doc["temp"] = temp;
  doc["lat"] = lat;
  doc["lon"] = lon;
  doc["alt"] = alt;
  doc["rssi"] = rssi;
  doc["snr"] = snr;
  
  // Create nested arrays for 3-axis data
  // "to<JsonArray>()" is the cleaner v7 way to create arrays, though createNestedArray also works
  JsonArray accel = doc["accel"].to<JsonArray>();
  accel.add(ax);
  accel.add(ay);
  accel.add(az);

  JsonArray gyro = doc["gyro"].to<JsonArray>();
  gyro.add(gx);
  gyro.add(gy);
  gyro.add(gz);

  JsonArray mag = doc["mag"].to<JsonArray>();
  mag.add(mx);
  mag.add(my);
  mag.add(mz);

  // Serialize to Serial (Output to monitor)
  serializeJson(doc, Serial);
  Serial.println(); // Newline is crucial for the Python reader to detect the end of packet
}

void loop() {
  // --- SIMULATION LOGIC (Replace with your LoRa receive code) ---
  
  // Update simulation values
  simAlt += 0.5;
  simLat += 0.0001;
  simLon += 0.0001;
  simTemp = 25.0 + sin(millis() / 10000.0);
  
  // Simulate 3-axis data (Example dummy values)
  simaX += 0.001; simaY += 0.002; simaZ += 0.0005;
  simgX += 0.0001; simgY += 0.0002; simgZ += 0.0001;
  simmX += 0.01; simmY += 0.015; simmZ += 0.02;

  simRssi = -70.0 + 5.0 * sin(millis() / 15000.0);
  simSnr = 7.0 + 2.0 * cos(millis() / 20000.0);

  // CALL THE FUNCTION
  sendTelemetry(millis(), simTemp, simLat, simLon, simAlt, 
                simaX, simaY, simaZ, 
                simgX, simgY, simgZ, 
                simmX, simmY, simmZ, simRssi, simSnr);

  delay(1000);
}