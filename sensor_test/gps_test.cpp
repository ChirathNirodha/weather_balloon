#include <TinyGPS++.h>
#include <HardwareSerial.h>

// Create the GPS object
TinyGPSPlus gps;

// Create the Hardware Serial connection
HardwareSerial GPS_Serial(2);

void setup() {
  // 1. Start the connection to your computer
  Serial.begin(115200);
  
  // 2. Start the connection to the GPS module
  // RX pin 16, TX pin 17, 9600 Baud rate
  GPS_Serial.begin(9600, SERIAL_8N1, 16, 17);

  Serial.println("GPS Ready. Waiting for satellite data...");
}

void loop() {
  // This reads data from the GPS whenever it is available
  while (GPS_Serial.available() > 0) {
    
    // If the GPS sends a valid message, we process it here:
    if (gps.encode(GPS_Serial.read())) {
      
      // ONLY print if we have a valid location found
      if (gps.location.isValid()) {
        Serial.print("Latitude: ");
        Serial.print(gps.location.lat(), 6);
        Serial.print(" | Longitude: ");
        Serial.println(gps.location.lng(), 6);
      } 
      else {
        Serial.println("GPS is connected but searching for satellites...");
      }
    }
  }
}