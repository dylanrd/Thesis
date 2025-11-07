import serial
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
matplotlib.use('TkAgg')

# --- CONFIGURATION ---
cols, rows = 48, 32  # Total sensors = 210
total_sensors = cols * rows
baseline_frames = 10  # Number of frames to average for baseline
MIN_RESISTANCE_DELTA = 10000.0  # Resistance change threshold (ohms) to ignore

# --- SETUP ---
arduinoData = serial.Serial('com11', 115200, timeout=0.1)
arduinoData.reset_input_buffer()
fig, ax = plt.subplots()
plt.ion()
heatmap = ax.imshow(np.zeros((cols, rows)), cmap='plasma', vmin=0, vmax=1)
plt.colorbar(heatmap)

current_readings = np.zeros(total_sensors, dtype=float)
baseline_buffer = []
baseline_conductance = np.zeros(total_sensors, dtype=float)
baseline_collected = False

print("📡 Collecting baseline... Please ensure mat is empty.")


# --- UTILITY FUNCTIONS ---
def replace_zeros_with_next_valid(arr):
    arr = arr.copy()
    for i in range(len(arr)):
        if arr[i] <= 0:
            # Look forward for a valid value
            for j in range(i + 1, len(arr)):
                if arr[j] > 0:
                    arr[i] = arr[j]
                    break
    return arr

def read_serial_data_safely(serial_conn):
    """Read serial data with reduced latency and line parsing."""
    try:
        lines = []
        # Read a small burst of lines to keep latency low
        for _ in range(64):
            line = serial_conn.readline()
            if not line:
                break
            lines.append(line)
        if not lines:
            return None
        
        valid_readings = []
        for raw in lines:
            try:
                text = raw.decode('utf-8', errors='ignore').strip()
                if not text:
                    continue
                parts = text.split(',')
                if len(parts) != 2:
                    continue
                resistance = float(parts[0])
                index = int(parts[1])
                valid_readings.append((resistance, index))
            except Exception:
                continue
        return valid_readings if valid_readings else None
    except Exception as e:
        print(f"⚠️ Serial read error: {e}")
        return None


# --- MAIN LOOP ---
while True:
    try:
        # Use the new safe reading function
        readings = read_serial_data_safely(arduinoData)
        
        if readings is None:
            continue
            
        # Process all valid readings from this batch
        frame_complete = False
        for resistance, index in readings:
            if index < 0 or index >= total_sensors:
                continue  # Skip invalid indices

            current_readings[index] = resistance
            
            # Frame boundary: index 0 indicates start of new frame
            if index == 0:
                frame_complete = True

        # Process frame if complete
        if frame_complete:
            # Replace bad (zero/negative) readings
            fixed_readings = replace_zeros_with_next_valid(current_readings)
            # Compute conductance safely
            with np.errstate(divide='ignore', invalid='ignore'):
                conductance = np.where(fixed_readings > 0, 1.0 / fixed_readings, 0.0)

            if not np.all(np.isfinite(conductance)):
                print("⚠️ Skipping frame: non-finite conductance detected.")
                continue

            if not baseline_collected:
                baseline_buffer.append(conductance.copy())
                print(f"📊 Capturing baseline frame {len(baseline_buffer)} / {baseline_frames}")
                if len(baseline_buffer) >= baseline_frames:
                    baseline_conductance = np.mean(baseline_buffer, axis=0)
                    baseline_collected = True
                    print("✅ Baseline collected. You may now step on the mat.")
                continue

            # Suppress small resistance changes by keeping baseline resistance
            # Convert baseline conductance back to resistance for comparison
            with np.errstate(divide='ignore', invalid='ignore'):
                baseline_resistance = np.where(baseline_conductance > 0, 1.0 / baseline_conductance, 0.0)
            
            # Calculate resistance difference
            resistance_delta = np.abs(fixed_readings - baseline_resistance)
            
            # Keep baseline resistance for small changes
            small_change_mask = resistance_delta < MIN_RESISTANCE_DELTA
            adjusted_resistance = fixed_readings.copy()
            adjusted_resistance[small_change_mask] = baseline_resistance[small_change_mask]
            
            # Convert back to conductance for pressure calculation
            with np.errstate(divide='ignore', invalid='ignore'):
                adjusted_conductance = np.where(adjusted_resistance > 0, 1.0 / adjusted_resistance, 0.0)

            # Compute pressure difference (positive deltas only)
            pressure_map = adjusted_conductance - baseline_conductance
            pressure_map = np.clip(pressure_map, 0, None)

            # Normalize to [0, 1] for display
            max_val = np.max(pressure_map)
            normalized = pressure_map / max_val if max_val > 0 else pressure_map

            # Update heatmap
            heatmap_data = normalized.reshape((cols, rows))
            heatmap.set_data(heatmap_data)
            plt.draw()
            plt.pause(0.001)

    except (ValueError, IndexError, UnicodeDecodeError) as e:
        print(f"⚠️ Skipping bad input: {e}")
        continue
