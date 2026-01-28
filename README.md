# Weather Balloon Ground Station

## 1. Firmware (ESP32 / Arduino)
This project uses **PlatformIO**. 
1. Open the project folder in VS Code.
2. PlatformIO will automatically install the correct libraries (ArduinoJson, Adafruit MAX31865, etc.) based on `platformio.ini`.
3. Click the "Upload" arrow.

## 2. Ground Station (Python Bridge)
**Prerequisites:**
* Python 3.10 or newer (Code is patched for Python 3.13+)
* Google Chrome (for the dashboard)

**Setup:**
1.  Open a terminal in the project folder.
2.  Create a virtual environment (keeps libraries isolated):
    ```bash
    python -m venv venv
    ```
3.  Activate it:
    * **Windows:** `venv\Scripts\activate`
    * **Mac/Linux:** `source venv/bin/activate`
4.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

**Running:**
1.  Connect the Arduino/ESP32.
2.  Update `SERIAL_PORT` in `serial_bridge.py` if necessary.
3.  Run the bridge:
    ```bash
    python serial_bridge.py
    ```
4.  Open `weather_balloon_tracker.html` in your browser.