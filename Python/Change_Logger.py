import serial
import time
import csv
import numpy as np
import os
from datetime import datetime

# Configuration
SERIAL_PORT = 'com11'
BAUD_RATE = 115200
ROWS, COLS = 48, 32
TOTAL_SENSORS = ROWS * COLS

# Threshold settings
THRESHOLD_ENABLED = True
RESISTANCE_CHANGE_THRESHOLD = 10000.0  # Ohms - adjust as needed
MIN_CHANGE_THRESHOLD = 1000.0  # Minimum change to log (reduces noise)

# Data collection settings
FRAME_TIMEOUT = 0.1  # seconds - how long to wait for a complete frame
LOG_ALL_DATA = False  # Set to True to log all data regardless of threshold

# Create timestamped output folder
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_folder = f"change_log_{timestamp}"
os.makedirs(output_folder, exist_ok=True)

# Log files
log_file = os.path.join(output_folder, "resistance_changes.csv")
threshold_log_file = os.path.join(output_folder, "threshold_events.csv")

print(f"📁 Created output folder: {output_folder}")
print(f"📊 Sensor array: {ROWS} rows × {COLS} columns = {TOTAL_SENSORS} sensors")
print(f"⚙️ Threshold: {'Enabled' if THRESHOLD_ENABLED else 'Disabled'} ({RESISTANCE_CHANGE_THRESHOLD} Ohms)")

# Connect to Arduino
try:
    arduinoData = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"✅ Connected to Arduino on {SERIAL_PORT}")
except serial.SerialException as e:
    print(f"❌ Failed to connect to Arduino: {e}")
    print("Please check:")
    print("1. Arduino is connected to COM11")
    print("2. No other programs are using the serial port")
    print("3. Arduino is powered on")
    exit(1)

# Initialize data structures
frame_buffer = {}  # Store current frame data
last_frame_time = time.time()
frame_count = 0
baseline_collected = False
baseline = np.zeros(TOTAL_SENSORS, dtype=float)
baseline_frames_collected = 0
baseline_frames_needed = 10

# Open log files
print("📝 Logging started")
with open(log_file, mode="a", newline="") as file, \
     open(threshold_log_file, mode="a", newline="") as threshold_file:
    
    writer = csv.writer(file)
    threshold_writer = csv.writer(threshold_file)
    
    # Write headers
    if file.tell() == 0:
        writer.writerow(["Timestamp", "Sensor ID", "Resistance Change (Ohms)", "Frame Number"])
    if threshold_file.tell() == 0:
        threshold_writer.writerow(["Timestamp", "Sensor ID", "Resistance Change (Ohms)", "Frame Number", "Threshold Exceeded"])

    print("🔄 Waiting for baseline collection to complete...")
    
    # Continuously read from the serial port
    while True:
        try:
            # Read a line of data from the serial port
            line = arduinoData.readline().decode("utf-8").strip()
            if not line:
                continue  # Skip empty lines

            # Check for status messages (skip them)
            if "Baseline collection complete" in line or "Baseline collection:" in line:
                continue

            # Parse the sensor data
            parts = line.split(",")
            if len(parts) != 2:
                continue

            resistance_change = float(parts[0])
            sensor_id = int(parts[1])
            
            # Validate sensor ID
            if sensor_id < 0 or sensor_id >= TOTAL_SENSORS:
                continue

            # Add to frame buffer
            frame_buffer[sensor_id] = resistance_change
            
            # Check if we should process the current frame
            current_time = time.time()
            time_since_last_frame = current_time - last_frame_time
            
            # Process frame if we have enough data or timeout occurred
            if (len(frame_buffer) >= TOTAL_SENSORS * 0.8 or  # 80% of sensors updated
                time_since_last_frame > FRAME_TIMEOUT):  # Timeout
                
                # Handle baseline collection
                if not baseline_collected:
                    # Collect baseline data
                    for sensor_id, resistance_change in frame_buffer.items():
                        baseline[sensor_id] += resistance_change
                    
                    baseline_frames_collected += 1
                    percentage = (baseline_frames_collected / baseline_frames_needed) * 100
                    print(f"📊 Baseline collection: {baseline_frames_collected}/{baseline_frames_needed} ({percentage:.0f}%)")
                    
                    # Check if baseline collection is complete
                    if baseline_frames_collected >= baseline_frames_needed:
                        # Calculate average baseline
                        baseline = baseline / baseline_frames_needed
                        baseline_collected = True
                        print("✅ Baseline collection complete! Starting data logging...")
                    
                    # Clear frame buffer and continue
                    frame_buffer.clear()
                    last_frame_time = current_time
                    continue
                
                # Normal operation - log data
                frame_count += 1
                timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                
                # Process each sensor in the frame
                for sensor_id, resistance_change in frame_buffer.items():
                    # Apply minimum change filter
                    if abs(resistance_change) < MIN_CHANGE_THRESHOLD:
                        continue
                    
                    # Log all data if enabled
                    if LOG_ALL_DATA:
                        writer.writerow([timestamp_str, sensor_id, resistance_change, frame_count])
                    
                    # Check threshold
                    threshold_exceeded = abs(resistance_change) > RESISTANCE_CHANGE_THRESHOLD
                    
                    # Log threshold events
                    if THRESHOLD_ENABLED and threshold_exceeded:
                        threshold_writer.writerow([
                            timestamp_str, 
                            sensor_id, 
                            resistance_change, 
                            frame_count,
                            "YES"
                        ])
                        print(f"🚨 Threshold exceeded: Sensor {sensor_id}, Change: {resistance_change:.1f} Ohms")
                    
                    # Log all data if threshold is disabled
                    elif not THRESHOLD_ENABLED:
                        writer.writerow([timestamp_str, sensor_id, resistance_change, frame_count])
                
                # Clear frame buffer and update timing
                frame_buffer.clear()
                last_frame_time = current_time
                
                # Show progress every 100 frames
                if frame_count % 100 == 0:
                    print(f"📈 Processed {frame_count} frames")

        except KeyboardInterrupt:
            print("\n🛑 Logging stopped by user")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            continue

print(f"✅ Logging complete!")
print(f"📁 Data saved to: {output_folder}/")
print(f"📊 Total frames processed: {frame_count}")
print(f"📝 All data: {log_file}")
print(f"🚨 Threshold events: {threshold_log_file}")
