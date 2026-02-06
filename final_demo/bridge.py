import asyncio
import websockets
import serial
import json
import time
import csv
import os
import random
import math

# --- CONFIGURATION ---
# UPDATE THIS TO YOUR ACTUAL PORT!
SERIAL_PORT = 'COM3'  
BAUD_RATE = 9600
SERVER_PORT = 8101
CSV_FILENAME = 'telemetry_log.csv'
CLIENTS = set()

# --- CSV LOGGING FUNCTION ---
def init_csv():
    file_exists = os.path.isfile(CSV_FILENAME)
    if not file_exists:
        with open(CSV_FILENAME, mode='w', newline='') as f:
            writer = csv.writer(f)
            headers = [
                'Timestamp', 'Temp_C', 'Lat', 'Lon', 'Alt_m',
                'Accel_X', 'Accel_Y', 'Accel_Z',
                'Gyro_X', 'Gyro_Y', 'Gyro_Z',
                'Mag_X', 'Mag_Y', 'Mag_Z'
            ]
            writer.writerow(headers)

def log_to_csv(data_dict):
    try:
        with open(CSV_FILENAME, mode='a', newline='') as f:
            writer = csv.writer(f)
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
                mag[0], mag[1], mag[2]
            ]
            writer.writerow(row)
    except Exception as e:
        print(f"CSV Error: {e}")

# --- SERIAL & SIMULATION ---

def setup_serial():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
        time.sleep(2)
        ser.reset_input_buffer()
        print(f"✅ Successfully connected to {SERIAL_PORT}")
        return ser
    except serial.SerialException as e:
        print(f"⚠️  WARNING: Could not open {SERIAL_PORT}.")
        print(f"👉 Starting in SIMULATION MODE (generating fake data).")
        return None

def generate_fake_data():
    """Generates random data for testing the UI"""
    t = time.time() * 1000
    return {
        "timestamp": t,
        "temp": 25 + math.sin(t/10000) * 5,
        "lat": 7.8731 + (math.sin(t/5000) * 0.001),
        "lon": 80.7718 + (math.cos(t/5000) * 0.001),
        "alt": 100 + (t % 10000) / 10,
        "speed": random.uniform(10, 30),
        "rssi": random.randint(-90, -40),
        "snr": random.uniform(5, 12),
        "accel": [random.uniform(-1, 1), random.uniform(-1, 1), 9.8],
        "gyro": [random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1)],
        "mag": [random.uniform(20, 50), random.uniform(20, 50), random.uniform(20, 50)]
    }

def get_telemetry_packet(ser):
    # 1. Real Hardware Mode
    if ser:
        try:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line.startswith('{'):
                    try:
                        data = json.loads(line)
                        print(f"Rx: {line}")
                        log_to_csv(data)
                        return line
                    except json.JSONDecodeError:
                        pass
        except Exception:
            pass
        return None
    
    # 2. Simulation Mode (if no hardware)
    else:
        time.sleep(1.0) # Send data every second
        fake_data = generate_fake_data()
        json_str = json.dumps(fake_data)
        print(f"Simulating: {json_str}")
        return json_str

# --- WEBSOCKET SERVER ---

async def register(websocket):
    CLIENTS.add(websocket)

async def unregister(websocket):
    CLIENTS.remove(websocket)

async def producer_handler(ser):
    while True:
        packet = get_telemetry_packet(ser)
        if packet and CLIENTS:
            message = packet.encode('utf-8')
            tasks = [asyncio.create_task(client.send(message)) for client in CLIENTS]
            if tasks:
                await asyncio.wait(tasks, timeout=1)
        
        # If real hardware, check fast. If simulation, sleep is handled in generation.
        if ser:
            await asyncio.sleep(0.01)
        else:
            await asyncio.sleep(0.1)

async def websocket_handler(websocket, ser):
    await register(websocket)
    try:
        await websocket.wait_closed()
    finally:
        await unregister(websocket)

async def main():
    print("Starting Ground Station Bridge...")
    init_csv()
    
    # Try to connect to Serial, otherwise fall back to Simulation
    ser = setup_serial()

    try:
        start_server = websockets.serve(
            lambda websocket: websocket_handler(websocket, ser), 
            "localhost", 
            SERVER_PORT
        )
        print(f"WebSocket Server running on port {SERVER_PORT}")
        await start_server
        await producer_handler(ser)
    except OSError as e:
        if e.errno == 48: 
             print(f"❌ Error: Port {SERVER_PORT} is busy. Stop the previous Python script!")
             return
        raise e

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped.")