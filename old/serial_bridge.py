import asyncio
import websockets
import serial
import json
import time

# --- CONFIGURATION ---
SERIAL_PORT = '/dev/cu.usbmodem5AE70285671' # Add the correct COM port # Updated to match your successful connection
BAUD_RATE = 9600
SERVER_PORT = 8101
CLIENTS = set()

# --- SERIAL COMMUNICATION ---

def setup_serial():
    try:
        # Reduced timeout to 0.1s to prevent blocking the WebSocket loop
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
        time.sleep(2)
        ser.reset_input_buffer()
        print(f"Successfully connected to {SERIAL_PORT}")
        return ser
    except serial.SerialException as e:
        print(f"CRITICAL: Could not open serial port {SERIAL_PORT}. Error: {e}")
        return None

def get_telemetry_packet(ser):
    try:
        # Attempt to read a line
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            if not line: return None
            
            # Check for JSON start
            if line.startswith('{'):
                try:
                    json.loads(line) # Validate JSON
                    print(f"Sent packet: {line}")
                    return line
                except json.JSONDecodeError:
                    return None
        return None
    except Exception:
        return None

# --- WEBSOCKET SERVER ---

async def register(websocket):
    CLIENTS.add(websocket)
    print(f"Client connected. Total: {len(CLIENTS)}")

async def unregister(websocket):
    CLIENTS.remove(websocket)
    print(f"Client disconnected. Total: {len(CLIENTS)}")

async def producer_handler(ser):
    while True:
        packet = get_telemetry_packet(ser)
        if packet and CLIENTS:
            # FIX: Send as raw string, NOT bytes. 
            # The browser expects a text string for JSON.parse()
            message = packet 
            
            # Create tasks for Python 3.11+
            tasks = [asyncio.create_task(client.send(message)) for client in CLIENTS]
            if tasks:
                await asyncio.wait(tasks, timeout=1)
        
        await asyncio.sleep(0.1)

async def websocket_handler(websocket):
    await register(websocket)
    try:
        # Keep connection open
        await websocket.wait_closed()
    finally:
        await unregister(websocket)

async def main():
    print("Starting WebSocket Server...")
    ser = setup_serial()
    if not ser: return

    # Start the WebSocket server
    async with websockets.serve(websocket_handler, "localhost", SERVER_PORT):
        await producer_handler(ser)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped.")