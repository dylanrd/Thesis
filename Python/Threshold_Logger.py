import serial
import time
import csv
import numpy as np
import os
from datetime import datetime
import threading
import queue
from collections import deque

# Configuration
SERIAL_PORT = 'com11'
BAUD_RATE = 2000000
ROWS, COLS = 48, 48
TOTAL_SENSORS = ROWS * COLS

# Threshold settings
RESISTANCE_CHANGE_THRESHOLD = 5000.0  # Ohms - only log changes above this
BASELINE_FRAMES = 10  # Number of frames to collect for baseline

# Serial reading configuration
READING_METHOD = "threaded"  # Options: "buffered", "alternative", "threaded", "reconstruct"
ENABLE_DIAGNOSTICS = True  # Set to True to show data corruption statistics
BUFFER_SIZE = 65536  # Buffer size for threaded reading

# Create timestamped output folder
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_folder = f"threshold_log_{timestamp}"
os.makedirs(output_folder, exist_ok=True)

# Log files
log_file = os.path.join(output_folder, "threshold_changes.csv")
baseline_file = os.path.join(output_folder, "baseline_values.csv")

print(f"📁 Created output folder: {output_folder}")
print(f"📊 Sensor array: {ROWS} rows × {COLS} columns = {TOTAL_SENSORS} sensors")
print(f"⚙️ Threshold: {RESISTANCE_CHANGE_THRESHOLD} Ohms")

# Connect to Arduino with optimized settings for high baud rate
try:
    arduinoData = serial.Serial(
        port=SERIAL_PORT,
        baudrate=BAUD_RATE,
        timeout=0,  # Non-blocking reads
        write_timeout=0,  # Non-blocking writes
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        xonxoff=False,  # Disable software flow control
        rtscts=False,   # Disable hardware flow control
        dsrdtr=False,   # Disable DSR/DTR flow control
        inter_byte_timeout=None  # No timeout between bytes
    )
    
    # Optimize buffer sizes for high-speed communication
    arduinoData.reset_input_buffer()
    arduinoData.reset_output_buffer()
    
    # Set larger read buffer if supported (Windows)
    try:
        arduinoData.set_buffer_size(rx_size=65536, tx_size=65536)
    except:
        pass  # Not supported on all systems
    
    print(f"✅ Connected to Arduino on {SERIAL_PORT} at {BAUD_RATE} baud")
    print(f"📊 Buffer sizes: RX={arduinoData.in_waiting}, TX={arduinoData.out_waiting}")
    
except serial.SerialException as e:
    print(f"❌ Failed to connect to Arduino: {e}")
    print("Please check:")
    print("1. Arduino is connected to COM11")
    print("2. No other programs are using the serial port")
    print("3. Arduino is powered on")
    print("4. Try reducing baud rate if connection fails")
    exit(1)

# Initialize data structures
current_readings = np.zeros(TOTAL_SENSORS, dtype=float)
baseline_resistance = np.zeros(TOTAL_SENSORS, dtype=float)
baseline_collected = False
baseline_frames_collected = 0

# Diagnostic counters
if ENABLE_DIAGNOSTICS:
    total_lines_read = 0
    valid_lines_parsed = 0
    corrupted_lines = 0
    incomplete_lines = 0
    last_diagnostic_time = time.time()

class ThreadedSerialReader:
    """High-performance threaded serial reader for high baud rates."""
    
    def __init__(self, serial_conn, buffer_size=65536):
        self.serial_conn = serial_conn
        self.buffer_size = buffer_size
        self.data_queue = queue.Queue(maxsize=1000)  # Limit queue size to prevent memory issues
        self.running = False
        self.thread = None
        self.raw_buffer = b''
        
    def start(self):
        """Start the reading thread."""
        self.running = True
        self.thread = threading.Thread(target=self._read_loop, daemon=True)
        self.thread.start()
        
    def stop(self):
        """Stop the reading thread."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
            
    def _read_loop(self):
        """Main reading loop running in separate thread."""
        while self.running:
            try:
                if self.serial_conn.in_waiting > 0:
                    # Read all available data
                    data = self.serial_conn.read(self.serial_conn.in_waiting)
                    if data:
                        self.raw_buffer += data
                        
                        # Process complete lines
                        while b'\n' in self.raw_buffer:
                            line, self.raw_buffer = self.raw_buffer.split(b'\n', 1)
                            if line.strip():
                                try:
                                    self.data_queue.put_nowait(line)
                                except queue.Full:
                                    # Queue is full, remove oldest item
                                    try:
                                        self.data_queue.get_nowait()
                                        self.data_queue.put_nowait(line)
                                    except queue.Empty:
                                        pass
                else:
                    time.sleep(0.001)  # Small delay to prevent busy waiting
                    
            except Exception as e:
                if ENABLE_DIAGNOSTICS:
                    print(f"⚠️ Threaded reader error: {e}")
                time.sleep(0.01)
                
    def get_readings(self):
        """Get available readings from the queue."""
        readings = []
        try:
            while True:
                line = self.data_queue.get_nowait()
                try:
                    text = line.decode('utf-8', errors='ignore').strip()
                    if not text or ',' not in text:
                        continue
                        
                    parts = text.split(',')
                    if len(parts) != 2:
                        continue
                        
                    resistance = float(parts[0])
                    index = int(parts[1])
                    
                    if 0 <= resistance <= 1000000 and 0 <= index < TOTAL_SENSORS:
                        readings.append((resistance, index))
                        
                except (ValueError, IndexError, UnicodeDecodeError):
                    if ENABLE_DIAGNOSTICS:
                        corrupted_lines += 1
                    continue
                    
        except queue.Empty:
            pass
            
        return readings if readings else None

class DataReconstructor:
    """Reconstructs split data packets from high-speed serial communication."""
    
    def __init__(self):
        self.buffer = b''
        self.complete_lines = deque()
        
    def add_data(self, data):
        """Add new data to the buffer and extract complete lines."""
        self.buffer += data
        
        # Extract complete lines
        while b'\n' in self.buffer:
            line, self.buffer = self.buffer.split(b'\n', 1)
            if line.strip():
                self.complete_lines.append(line)
                
    def get_complete_line(self):
        """Get the next complete line, or None if none available."""
        try:
            return self.complete_lines.popleft()
        except IndexError:
            return None
            
    def has_complete_lines(self):
        """Check if there are complete lines available."""
        return len(self.complete_lines) > 0

def read_serial_data_safely(serial_conn):
    """Read serial data with optimized buffering for high baud rates."""
    try:
        # Method 1: Buffered reading with larger buffer
        if serial_conn.in_waiting > 0:
            # Read all available data at once to minimize overhead
            raw_data = serial_conn.read(serial_conn.in_waiting)
            if not raw_data:
                return None
            
            # Split by newlines and process
            lines = raw_data.split(b'\n')
            valid_readings = []
            
            for line in lines:
                if not line:
                    continue
                    
                try:
                    # Handle potential incomplete lines (no newline at end)
                    if not line.endswith(b'\r') and not line.endswith(b'\n'):
                        # This might be an incomplete line, skip it
                        continue
                        
                    text = line.decode('utf-8', errors='ignore').strip()
                    if not text:
                        continue
                        
                    # More robust parsing with validation
                    if ',' not in text:
                        continue
                        
                    parts = text.split(',')
                    if len(parts) != 2:
                        continue
                        
                    # Validate numeric data
                    resistance_str = parts[0].strip()
                    index_str = parts[1].strip()
                    
                    if not resistance_str or not index_str:
                        continue
                        
                    resistance = float(resistance_str)
                    index = int(index_str)
                    
                    # Validate ranges
                    if resistance < 0 or resistance > 1000000:  # Reasonable resistance range
                        continue
                    if index < 0 or index >= TOTAL_SENSORS:
                        continue
                        
                    valid_readings.append((resistance, index))
                    
                except (ValueError, UnicodeDecodeError, IndexError):
                    # Skip malformed data silently
                    continue
                    
            return valid_readings if valid_readings else None
            
        return None
        
    except Exception as e:
        print(f"⚠️ Serial read error: {e}")
        return None

def read_serial_data_reconstruct(serial_conn, reconstructor):
    """Read serial data with packet reconstruction for split data."""
    try:
        if serial_conn.in_waiting > 0:
            # Read all available data
            raw_data = serial_conn.read(serial_conn.in_waiting)
            if raw_data:
                reconstructor.add_data(raw_data)
            
            # Process complete lines
            valid_readings = []
            while reconstructor.has_complete_lines():
                line = reconstructor.get_complete_line()
                if not line:
                    break
                    
                try:
                    text = line.decode('utf-8', errors='ignore').strip()
                    if not text or ',' not in text:
                        continue
                        
                    parts = text.split(',')
                    if len(parts) != 2:
                        continue
                        
                    resistance = float(parts[0])
                    index = int(parts[1])
                    
                    if 0 <= resistance <= 1000000 and 0 <= index < TOTAL_SENSORS:
                        valid_readings.append((resistance, index))
                        
                except (ValueError, UnicodeDecodeError, IndexError):
                    continue
                    
            return valid_readings if valid_readings else None
            
        return None
        
    except Exception as e:
        print(f"⚠️ Reconstruction read error: {e}")
        return None

def read_serial_data_alternative(serial_conn):
    """Alternative method: Line-by-line reading with timeout handling."""
    try:
        valid_readings = []
        lines_read = 0
        max_lines_per_batch = 128  # Increased batch size
        
        while lines_read < max_lines_per_batch:
            if serial_conn.in_waiting == 0:
                break
                
            line = serial_conn.readline()
            if not line:
                break
                
            lines_read += 1
            
            try:
                text = line.decode('utf-8', errors='ignore').strip()
                if not text:
                    continue
                    
                # Check for complete line (ends with expected format)
                if not (',' in text and text.count(',') == 1):
                    continue
                    
                parts = text.split(',')
                resistance = float(parts[0])
                index = int(parts[1])
                
                # Validate data ranges
                if 0 <= resistance <= 1000000 and 0 <= index < TOTAL_SENSORS:
                    valid_readings.append((resistance, index))
                    
            except (ValueError, IndexError, UnicodeDecodeError):
                print("Exception")
                continue
                
        return valid_readings if valid_readings else None
        
    except Exception as e:
        print(f"⚠️ Alternative serial read error: {e}")
        return None

def replace_zeros_with_next_valid(arr):
    """Replace zero/negative values with next valid value."""
    arr = arr.copy()
    for i in range(len(arr)):
        if arr[i] <= 0:
            # Look forward for a valid value
            for j in range(i + 1, len(arr)):
                if arr[j] > 0:
                    arr[i] = arr[j]
                    break
    return arr

print("📡 Collecting baseline... Please ensure mat is empty.")
print("Press Ctrl+C to stop logging")
print(f"🔧 Using reading method: {READING_METHOD}")

# Initialize reading method
threaded_reader = None
data_reconstructor = None

if READING_METHOD == "threaded":
    threaded_reader = ThreadedSerialReader(arduinoData, BUFFER_SIZE)
    threaded_reader.start()
    print("🚀 Threaded reader started")
elif READING_METHOD == "reconstruct":
    data_reconstructor = DataReconstructor()
    print("🔧 Data reconstruction enabled")

# Open log files
with open(log_file, mode="w", newline="") as log_csv, \
     open(baseline_file, mode="w", newline="") as baseline_csv:
    
    log_writer = csv.writer(log_csv)
    baseline_writer = csv.writer(baseline_csv)
    
    # Write headers
    log_writer.writerow(["Timestamp", "Sensor_ID", "Resistance_Ohms"])
    baseline_writer.writerow(["Sensor_ID", "Baseline_Resistance_Ohms"])
    
    try:
        while True:
            # Read serial data using selected method
            if READING_METHOD == "threaded":
                readings = threaded_reader.get_readings()
            elif READING_METHOD == "reconstruct":
                readings = read_serial_data_reconstruct(arduinoData, data_reconstructor)
            elif READING_METHOD == "buffered":
                readings = read_serial_data_safely(arduinoData)
            else:  # alternative
                readings = read_serial_data_alternative(arduinoData)
            
            if readings is None:
                continue
                
            # Update diagnostics
            if ENABLE_DIAGNOSTICS:
                valid_lines_parsed += len(readings)
                current_time = time.time()
                if current_time - last_diagnostic_time >= 10:  # Print every 10 seconds
                    print(f"📊 Data quality: {valid_lines_parsed} valid readings, "
                          f"{corrupted_lines} corrupted, {incomplete_lines} incomplete")
                    last_diagnostic_time = current_time
                
            # Process readings
            frame_complete = False
            for resistance, index in readings:
                if index < 0 or index >= TOTAL_SENSORS:
                    continue  # Skip invalid indices

                current_readings[index] = resistance
                
                # Frame boundary: index 0 indicates start of new frame
                if index == 0:
                    frame_complete = True

            # Process frame if complete
            if frame_complete:
                # Replace bad (zero/negative) readings
                fixed_readings = replace_zeros_with_next_valid(current_readings)
                
                # Debug: Check how many sensors we have data for
                sensors_with_data = np.count_nonzero(fixed_readings)
                if ENABLE_DIAGNOSTICS:
                    print(f"🔍 Frame data: {sensors_with_data}/{TOTAL_SENSORS} sensors have data")
                
                if not baseline_collected:
                    # Collect baseline
                    baseline_resistance = fixed_readings.copy()
                    baseline_frames_collected += 1
                    print(f"📊 Collecting baseline frame {baseline_frames_collected} / {BASELINE_FRAMES}")
                    
                    if baseline_frames_collected >= BASELINE_FRAMES:
                        # Calculate average baseline
                        baseline_resistance = fixed_readings.copy()  # Use last frame as baseline
                        baseline_collected = True
                        
                        # Save baseline to file
                        for sensor_id in range(TOTAL_SENSORS):
                            baseline_writer.writerow([sensor_id, baseline_resistance[sensor_id]])
                        
                        print("✅ Baseline collected. Starting threshold logging...")
                        print(f"📝 Baseline saved to: {baseline_file}")
                        print(f"📝 Changes will be logged to: {log_file}")
                        print(f"⚙️ Only logging changes > {RESISTANCE_CHANGE_THRESHOLD} Ohms")
                    continue
                
                # Logging phase - record baseline or actual resistance based on threshold
                timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                frame_logged = False
                sensors_logged = 0
                
                for sensor_id in range(TOTAL_SENSORS):
                    current_resistance = fixed_readings[sensor_id]
                    baseline_res = baseline_resistance[sensor_id]
                    
                    # Calculate resistance change
                    resistance_change = abs(current_resistance - baseline_res)
                    
                    # Record actual resistance if above threshold, otherwise baseline
                    if resistance_change > RESISTANCE_CHANGE_THRESHOLD:
                        recorded_resistance = current_resistance
                        frame_logged = True
                    else:
                        recorded_resistance = baseline_res
                    
                    # Always log every sensor
                    log_writer.writerow([
                        timestamp_str,
                        sensor_id,
                        recorded_resistance
                    ])
                    sensors_logged += 1
                
                # Verify we logged the correct number of sensors
                if ENABLE_DIAGNOSTICS:
                    print(f"📝 Logged {sensors_logged}/{TOTAL_SENSORS} sensors to CSV")
                
                # Show frame completion status
                if frame_logged:
                    print(f"📊 Frame logged: {timestamp_str} (threshold changes detected)")
                else:
                    print(f"📊 Frame logged: {timestamp_str} (baseline values)")
                
                # Flush to ensure data is written
                log_csv.flush()
                
    except KeyboardInterrupt:
        print("\n🛑 Logging stopped by user.")
        print(f"📁 Data saved in: {output_folder}")
        print(f"📊 Baseline: {baseline_file}")
        print(f"📊 Changes: {log_file}")
    except Exception as e:
        print(f"❌ Error during logging: {e}")
        print(f"📁 Partial data saved in: {output_folder}")
    finally:
        # Cleanup threaded reader
        if threaded_reader:
            print("🛑 Stopping threaded reader...")
            threaded_reader.stop()
