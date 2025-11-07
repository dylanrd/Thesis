import serial  # import Serial Library
import numpy as np  # Import numpy
import matplotlib
from matplotlib import pyplot as plt
import time
import sys

# Set matplotlib backend
matplotlib.use('TkAgg')

# Configuration
fiveV_lines = 16
read_lines = 16
total_sensors = fiveV_lines * read_lines

# Initialize arrays
tempF = []
pressure = []

# Try to connect to serial port
try:
    arduinoData = serial.Serial('com11', 115200, timeout=1)  # Creating our serial object named arduinoData
    print("✅ Connected to Arduino on COM11")
except serial.SerialException as e:
    print(f"❌ Failed to connect to Arduino: {e}")
    print("Please check:")
    print("1. Arduino is connected to COM11")
    print("2. No other programs are using the serial port")
    print("3. Arduino is powered on")
    sys.exit(1)

# Setup matplotlib
fig, ax = plt.subplots(figsize=(10, 8))
heatmap = ax.imshow(np.zeros((fiveV_lines, read_lines)), cmap='plasma', vmin=0, vmax=1)
plt.colorbar(heatmap, label='Normalized Pressure')
ax.set_title('Force Resistive Sensor Array')
ax.set_xlabel('Sensor Columns')
ax.set_ylabel('Sensor Rows')
plt.ion()  # Turn on interactive mode

# Initialize variables
cnt = 0
sensorTracker = 0
initialiser = 0
baseline_frames = 10
baseline_buffer = []
baseline_collected = False

# Arrays for sensor data
baseline = np.zeros(total_sensors, dtype=float)
current = np.zeros(total_sensors, dtype=float)

print("📡 Collecting baseline data... Please ensure mat is empty.")
print("Press Ctrl+C to exit")

try:
    while True:  # Main data collection loop
        try:
            # Read data from serial port
            arduinoString = arduinoData.readline()
            
            # Skip empty lines
            if not arduinoString:
                continue
                
            # Decode and parse data
            dataArray = arduinoString.decode('utf-8').strip().split(',')
            
            # Validate data format
            if len(dataArray) != 2:
                continue
                
            # Parse values with error handling
            try:
                resistance = float(dataArray[0])
                index = int(dataArray[1])
            except (ValueError, IndexError):
                continue
                
            # Validate index range
            if index < 0 or index >= total_sensors:
                continue
                
            # Store current reading
            current[index] = resistance
            
            # Process when we have a complete frame (index 0 indicates new frame)
            if index == 0:
                # Replace any zero or negative values with small positive values
                current_fixed = np.where(current <= 0, 1e-6, current)
                
                # Convert resistance to conductance (1/R)
                with np.errstate(divide='ignore', invalid='ignore'):
                    conductance = np.where(current_fixed > 0, 1.0 / current_fixed, 0.0)
                
                # Check for valid conductance values
                if not np.all(np.isfinite(conductance)):
                    print("⚠️ Skipping frame: invalid conductance values detected")
                    continue
                
                # Baseline collection phase
                if not baseline_collected:
                    baseline_buffer.append(conductance.copy())
                    print(f"📊 Collecting baseline frame {len(baseline_buffer)} / {baseline_frames}")
                    
                    if len(baseline_buffer) >= baseline_frames:
                        baseline = np.mean(baseline_buffer, axis=0)
                        baseline_collected = True
                        print("✅ Baseline collected. You may now step on the mat.")
                    continue
                
                # Normal operation: compute pressure difference
                pressure_difference = conductance - baseline
                pressure_difference = np.clip(pressure_difference, 0, None)  # Only positive pressure
                
                # Normalize to [0, 1] for visualization
                max_pressure = np.max(pressure_difference)
                if max_pressure > 0:
                    normalized_pressure = pressure_difference / max_pressure
                else:
                    normalized_pressure = pressure_difference
                
                # Reshape for heatmap display
                heatmap_data = normalized_pressure.reshape((fiveV_lines, read_lines))
                
                # Update the heatmap
                heatmap.set_data(heatmap_data)
                heatmap.set_clim(0, 1)  # Set color limits
                
                # Update display
                plt.draw()
                plt.pause(0.01)
                
        except serial.SerialTimeoutException:
            print("⚠️ Serial timeout - no data received")
            continue
        except UnicodeDecodeError:
            print("⚠️ Unicode decode error - skipping malformed data")
            continue
        except Exception as e:
            print(f"⚠️ Unexpected error: {e}")
            continue
            
except KeyboardInterrupt:
    print("\n🛑 Plotter stopped by user")
    arduinoData.close()
    plt.close('all')
    sys.exit(0)
except Exception as e:
    print(f"❌ Fatal error: {e}")
    arduinoData.close()
    plt.close('all')
    sys.exit(1)
