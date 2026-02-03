#include <Wire.h>
#include <LSM6.h>
#include <LIS3MDL.h>

// Instantiate sensor objects
LSM6 imu;
LIS3MDL mag;

// I2C Pins for ESP32 (Default)
#define I2C_SDA 21
#define I2C_SCL 22

void setup() {
  Serial.begin(115200);
  
  // Initialize I2C with specific pins for ESP32
  Wire.begin(I2C_SDA, I2C_SCL);

  // Initialize IMU (Gyro + Accel)
  if (!imu.init()) {
    Serial.println("Failed to detect and initialize IMU (LSM6)!");
    while (1);
  }
  imu.enableDefault();

  // Initialize Magnetometer
  if (!mag.init()) {
    Serial.println("Failed to detect and initialize Magnetometer (LIS3MDL)!");
    while (1);
  }
  mag.enableDefault();
  
  Serial.println("Pololu MinIMU-9 v5/v6 initialized successfully.");
  delay(1000);
}

void loop() {
  // Read all sensors
  imu.read();
  mag.read();

  // Print Accelerometer (A), Gyro (G), and Magnetometer (M) values
  // Format: A: x, y, z | G: x, y, z | M: x, y, z
  
  Serial.print("A: ");
  Serial.print(imu.a.x); Serial.print(", ");
  Serial.print(imu.a.y); Serial.print(", ");
  Serial.print(imu.a.z);
  
  Serial.print(" | G: ");
  Serial.print(imu.g.x); Serial.print(", ");
  Serial.print(imu.g.y); Serial.print(", ");
  Serial.print(imu.g.z);
  
  Serial.print(" | M: ");
  Serial.print(mag.m.x); Serial.print(", ");
  Serial.print(mag.m.y); Serial.print(", ");
  Serial.print(mag.m.z);
  
  Serial.println();

  delay(100);
}