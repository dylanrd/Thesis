import serial
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
import time
import sys

# Set matplotlib backend
matplotlib.use('TkAgg')

# Configuration (same as plotter2.py)
cols, rows = 48, 32  # Total sensors = 1536
total_sensors = cols * rows

# Threshold settings
THRESHOLD_ENABLED = True
RESISTANCE_CHANGE_THRESHOLD = 1000.0  # Ohms - adjust as needed
MIN_CHANGE_THRESHOLD = 5.0  # Minimum change to display

# Initialize arrays
current_readings = np.zeros(total_sensors, dtype=float)
baseline = np.zeros(total_sensors, dtype=float)
frame_buffer = {}  # Store readings for current frame
last_frame_time = time.time()
frame_timeout = 0.1  # 100ms timeout for frame completion
frame_count = 0
baseline_collected = False
baseline_frames_collected = 0
baseline_frames_needed = 10

# Try to connect to serial port
try:
    arduinoData = serial.Serial('com11', 115200, timeout=1)
    print("✅ Connected to Arduino on COM11")
except serial.SerialException as e:
    print(f"❌ Failed to connect to Arduino: {e}")
    print("Please check:")
    print("1. Arduino is connected to COM11")
    print("2. No other programs are using the serial port")
    print("3. Arduino is powered on")
    sys.exit(1)

# Setup matplotlib (same as plotter2.py)
fig, ax = plt.subplots()
heatmap = ax.imshow(np.zeros((cols, rows)), cmap='plasma', vmin=0, vmax=1)
plt.colorbar(heatmap)

print("📡 Waiting for baseline collection to complete...")
print(f"⚙️ Threshold: {'Enabled' if THRESHOLD_ENABLED else 'Disabled'} ({RESISTANCE_CHANGE_THRESHOLD} Ohms)")
print("Press Ctrl+C to exit")

def process_frame_with_baseline():
    """Process the current frame buffer with baseline subtraction and update display (same as plotter2.py)"""
    global current_readings, frame_buffer, frame_count
    
    if len(frame_buffer) == 0:
        return
    
    frame_count += 1
    
    # Update current readings with new data (already baseline-subtracted from Arduino)
    for sensor_id, resistance_change in frame_buffer.items():
        current_readings[sensor_id] = resistance_change
    
    # Convert resistance changes to pressure map (positive deltas only)
    pressure_map = np.clip(current_readings, 0, None)
    
    # Normalize to [0, 1] for display (same as plotter2.py)
    max_val = np.max(pressure_map)
    normalized = pressure_map / max_val if max_val > 0 else pressure_map
    
    # Update heatmap (same as plotter2.py)
    heatmap_data = normalized.reshape((cols, rows))
    heatmap.set_data(heatmap_data)
    
    # Update display (same as plotter2.py)
    plt.draw()
    plt.pause(0.01)
    
    # Clear frame buffer
    frame_buffer.clear()

try:
    while True:
        try:
            # Read data from serial port
            arduinoString = arduinoData.readline()
            
            # Skip empty lines
            if not arduinoString:
                continue
                
            # Decode and parse data
            dataArray = arduinoString.decode('utf-8').strip().split(',')
            
            # Check for status messages (skip them)
            if len(dataArray) == 1:
                continue
            
            # Validate data format
            if len(dataArray) != 2:
                continue
                
            # Parse values with error handling
            try:
                resistance_change = float(dataArray[0])
                index = int(dataArray[1])
            except (ValueError, IndexError):
                continue
                
            # Validate index range
            if index < 0 or index >= total_sensors:
                continue
            
            # Add to frame buffer
            frame_buffer[index] = resistance_change
            
            # Check if we should process the frame
            current_time = time.time()
            time_since_last_frame = current_time - last_frame_time
            
            # Process frame if we have enough data or timeout occurred
            if (len(frame_buffer) >= total_sensors * 0.8 or  # 80% of sensors updated
                time_since_last_frame > frame_timeout):  # Timeout
                
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
                        print("✅ Baseline collection complete! Starting visualization...")
                        print("🎯 Ready for pressure sensing")
                    
                    # Clear frame buffer and continue
                    frame_buffer.clear()
                    last_frame_time = current_time
                    continue
                
                # Normal operation - process frame with baseline subtraction
                process_frame_with_baseline()
                last_frame_time = current_time
                
        except serial.SerialTimeoutException:
            # Process frame on timeout
            if len(frame_buffer) > 0 and baseline_collected:
                process_frame_with_baseline()
            continue
        except UnicodeDecodeError:
            print("⚠️ Unicode decode error - skipping malformed data")
            continue
        except Exception as e:
            print(f"⚠️ Unexpected error: {e}")
            continue
            
except KeyboardInterrupt:
    print(f"\n🛑 Plotter stopped by user")
    print(f"📊 Total frames processed: {frame_count}")
    arduinoData.close()
    plt.close('all')
    sys.exit(0)
except Exception as e:
    print(f"❌ Fatal error: {e}")
    arduinoData.close()
    plt.close('all')
    sys.exit(1)
