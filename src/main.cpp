#include <Arduino.h>
#include <ArduinoJson.h> // Make sure to install "ArduinoJson" by Benoit Blanchon via Library Manager

// --- CONFIGURATION ---
const long BAUD_RATE = 9600;

// Globals for simulation
double currentLat = 40.7128;
double currentLon = -74.0060;
float currentAlt = 1000.0;
uint32_t currentTime = 0;
// We'll simulate these to test the dashboard gauges
float currentSpeed = 15.5; 
int currentRssi = -55;
float currentSnr = 8.2;

// Size estimation:
// We are sending ~6-7 fields. 256 bytes is sufficient for Uno (2KB RAM).
// Using StaticJsonDocument is slightly better for Uno to avoid heap fragmentation,
// but DynamicJsonDocument(256) works fine here too.
const size_t JSON_DOC_SIZE = 256; 

void setup() {
  Serial.begin(BAUD_RATE);
  // Wait a moment for Serial to stabilize
  delay(1000);
  // Optional: Debug message (might be missed if Python script isn't running yet)
  // Serial.println(F("Arduino Uno Telemetry Sender Initialized."));
}

void loop() {
    // 1. Update simulated data
    currentTime = millis();
    currentLat += 0.0001;  // Move North slightly
    currentLon -= 0.00005; // Move West slightly
    currentAlt += 2.5;     // Increase altitude

    // Simulate signal fluctuation
    currentRssi = -55 + random(-5, 5); 
    currentSnr = 8.0 + (random(-10, 10) / 10.0);

    // Reset simulation if it gets too far/high
    if (currentAlt > 15000.0) {
      currentAlt = 1000.0;
      currentLat = 40.7128;
      currentLon = -74.0060;
    }
    
    // 2. Create the JSON document
    // NOTE: If using ArduinoJson v7, you can just use JsonDocument doc;
    // For v6, we stick to DynamicJsonDocument or StaticJsonDocument.
    StaticJsonDocument<JSON_DOC_SIZE> doc;

    // 3. Populate fields MATCHING the HTML expectations
    doc["time"] = currentTime;
    doc["lat"] = currentLat;       // HTML expects 'lat'
    doc["lon"] = currentLon;       // HTML expects 'lon'
    doc["alt"] = currentAlt;       // HTML expects 'alt'
    doc["speed"] = currentSpeed;   // HTML expects 'speed'
    doc["rssi"] = currentRssi;     // HTML expects 'rssi'
    doc["snr"] = currentSnr;       // HTML expects 'snr'

    // 4. Serialize to Serial
    serializeJson(doc, Serial);
    
    // 5. Send a newline to indicate end of packet
    Serial.println();

    // Delay to prevent flooding the serial port (Arduino Uno buffer is small)
    delay(1000); 
}