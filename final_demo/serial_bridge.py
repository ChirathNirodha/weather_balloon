import asyncio
import websockets
import serial
import json
import time
import csv
import os

# --- CONFIGURATION ---
# Check your specific port! It might be 'COM3' on Windows or '/dev/cu.usbmodem...' on Mac.
SERIAL_PORT = '/dev/cu.usbmodem5AE70285671'  
BAUD_RATE = 9600
SERVER_PORT = 8101
CSV_FILENAME = 'telemetry_log.csv'
CLIENTS = set()

# --- CSV LOGGING FUNCTION ---
def init_csv():
    """Creates the CSV file with headers if it doesn't exist."""
    file_exists = os.path.isfile(CSV_FILENAME)
    if not file_exists:
        with open(CSV_FILENAME, mode='w', newline='') as f:
            writer = csv.writer(f)
            # Define headers matching the JSON structure
            headers = [
                'Timestamp', 'Temp_C', 'Lat', 'Lon', 'Alt_m',
                'Accel_X', 'Accel_Y', 'Accel_Z',
                'Gyro_X', 'Gyro_Y', 'Gyro_Z',
                'Mag_X', 'Mag_Y', 'Mag_Z',
                'RSSI', 'SNR', 'Speed'  # <--- Added Headers
            ]
            writer.writerow(headers)
            print(f"Created log file: {CSV_FILENAME}")

def log_to_csv(data_dict):
    """Writes a single data row to the CSV file."""
    try:
        with open(CSV_FILENAME, mode='a', newline='') as f:
            writer = csv.writer(f)
            
            # Extract lists safely
            accel = data_dict.get('accel', [0,0,0])
            gyro = data_dict.get('gyro', [0,0,0])
            mag = data_dict.get('mag', [0,0,0])

            row = [
                data_dict.get('timestamp', 0),
                data_dict.get('temp', 0),
                data_dict.get('lat', 0),
                data_dict.get('lon', 0),
                data_dict.get('alt', 0),
                accel[0], accel[1], accel[2],
                gyro[0], gyro[1], gyro[2],
                mag[0], mag[1], mag[2],
                data_dict.get('rssi', 0), # <--- Added RSSI data
                data_dict.get('snr', 0),   # <--- Added SNR data
                data_dict.get('speed', 0)   # <--- Added Speed data
            ]
            writer.writerow(row)
    except Exception as e:
        print(f"Error writing to CSV: {e}")

# --- SERIAL COMMUNICATION ---

def setup_serial():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
        time.sleep(2)
        ser.reset_input_buffer()
        print(f"Successfully connected to {SERIAL_PORT}")
        return ser
    except serial.SerialException as e:
        print(f"CRITICAL: Could not open serial port {SERIAL_PORT}. Error: {e}")
        return None

def get_telemetry_packet(ser):
    try:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if not line: return None
            
            if line.startswith('{'):
                try:
                    data = json.loads(line) # Validate JSON
                    print(f"Rx: {line}")
                    
                    # LOG TO CSV HERE
                    log_to_csv(data)
                    
                    return line
                except json.JSONDecodeError:
                    return None
        return None
    except Exception as e:
        print(f"Serial Error: {e}")
        return None

# --- WEBSOCKET SERVER ---

async def register(websocket):
    CLIENTS.add(websocket)

async def unregister(websocket):
    CLIENTS.remove(websocket)

async def producer_handler(ser):
    while True:
        # Read from serial and log to CSV
        packet = get_telemetry_packet(ser)
        
        # Forward to Web Interface
        if packet and CLIENTS:
            message = packet.encode('utf-8')
            tasks = [asyncio.create_task(client.send(message)) for client in CLIENTS]
            if tasks:
                await asyncio.wait(tasks, timeout=1)
        await asyncio.sleep(0.01) # Reduced sleep for faster response

async def websocket_handler(websocket, ser):
    await register(websocket)
    try:
        await websocket.wait_closed()
    finally:
        await unregister(websocket)

async def main():
    print("Starting Ground Station Bridge...")
    init_csv() # Initialize the CSV file
    
    ser = setup_serial()
    if not ser: return

    try:
        start_server = websockets.serve(
            lambda websocket: websocket_handler(websocket, ser), 
            "localhost", 
            SERVER_PORT
        )
        await start_server
        print(f"WebSocket Server running on port {SERVER_PORT}")
        await producer_handler(ser)
    except OSError as e:
        if e.errno == 48: # Address already in use
             print(f"Error: Port {SERVER_PORT} is busy. Kill previous Python process.")
             return
        raise e

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped.")