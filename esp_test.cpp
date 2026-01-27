#include <Arduino.h>
#include <ArduinoJson.h> // Library required: ArduinoJson

// --- CONFIGURATION ---
const long BAUD_RATE = 9600;

// Globals for simulation
double currentLat = 40.7128;
double currentLon = -74.0060;
float currentAlt = 1000.0;
uint32_t currentTime = 0;
uint8_t recoveryState = 0;

// The JSON document size for our 6 fields (use the ArduinoJson Assistant to calculate)
// We need enough space for 6 keys (e.g., "time", "longitude", etc.) and their values.
const size_t JSON_DOC_SIZE = 256; 

void setup() {
  Serial.begin(BAUD_RATE);
  delay(1000);
  Serial.println("ESP32 JSON Telemetry Sender Initialized.");
}

void loop() {
    // 1. Update simulated data
    currentTime = millis();
    currentLat += 0.0001; // Move North
    currentLon -= 0.00005; // Move West
    currentAlt += 5.0; // Increase altitude

    // Reset simulation if it gets too far
    if (currentAlt > 15000.0) {
      currentAlt = 1000.0;
      currentLat = 40.7128;
      currentLon = -74.0060;
    }
    
    // 2. Create the JSON document
    DynamicJsonDocument doc(JSON_DOC_SIZE);

    // Populate the fields from DATA_RECOVERY.csv
    // NOTE: We are using the exact field names (keys) from the CSV:
    // time, gps time, longitude, latitude, height, recovery state
    doc["time"] = currentTime;
    doc["gps time"] = currentTime + 5000;
    doc["longitude"] = currentLon;
    doc["latitude"] = currentLat;
    doc["height"] = currentAlt;
    doc["recovery state"] = recoveryState;

    // 3. Serialize the JSON document to the serial port
    // This writes the JSON string followed by a newline, which the Python script expects.
    size_t bytes_written = serializeJson(doc, Serial);

    // 4. Send the newline character to signal the end of the line/packet
    Serial.println();

    // Debugging print to confirm size
    Serial.print(F(" [Bytes: "));
    Serial.print(bytes_written);
    Serial.println(F("]"));

    delay(1000); // Send data every 1 second
}