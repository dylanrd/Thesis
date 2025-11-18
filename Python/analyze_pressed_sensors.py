import pandas as pd
import numpy as np
import os

# Configuration
log_folder = "threshold_log_20251116_143220"
threshold_file = os.path.join(log_folder, "threshold_changes.csv")
baseline_file = os.path.join(log_folder, "baseline_values.csv")

# Threshold for detecting significant pressure (percentage change from baseline)
PRESSURE_THRESHOLD_PERCENT = 10  # 10% increase in resistance indicates pressure
MIN_RESISTANCE_CHANGE = 5000  # Minimum absolute change in ohms to consider

print("Loading data...")
# Load threshold changes
df = pd.read_csv(threshold_file)
print(f"Loaded {len(df)} threshold change records")

# Load baseline values
baseline_df = pd.read_csv(baseline_file)
baseline_dict = dict(zip(baseline_df['Sensor_ID'], baseline_df['Baseline_Resistance_Ohms']))
print(f"Loaded baseline for {len(baseline_dict)} sensors")

# Group by timestamp to analyze each frame
grouped = df.groupby('Timestamp')

# Track which sensors were pressed
sensor_press_count = {}  # Count how many times each sensor was pressed
sensor_max_change = {}   # Track maximum change for each sensor
sensor_avg_change = {}   # Track average change for each sensor
sensor_readings = {}     # Store all readings for each sensor

print("\nAnalyzing sensor activations...")
total_frames = len(grouped)
frames_analyzed = 0

for timestamp, group in grouped:
    frames_analyzed += 1
    if frames_analyzed % 100 == 0:
        print(f"  Processed {frames_analyzed}/{total_frames} frames...")
    
    for _, row in group.iterrows():
        sensor_id = int(row['Sensor_ID'])
        current_resistance = row['Resistance_Ohms']
        
        if sensor_id in baseline_dict:
            baseline_resistance = baseline_dict[sensor_id]
            
            # Calculate change
            resistance_change = current_resistance - baseline_resistance
            percent_change = (resistance_change / baseline_resistance * 100) if baseline_resistance > 0 else 0
            
            # Check if sensor was pressed (significant increase in resistance)
            # For pressure sensors, increased pressure typically increases resistance
            is_pressed = (resistance_change > MIN_RESISTANCE_CHANGE) and (percent_change > PRESSURE_THRESHOLD_PERCENT)
            
            if is_pressed:
                if sensor_id not in sensor_press_count:
                    sensor_press_count[sensor_id] = 0
                    sensor_max_change[sensor_id] = resistance_change
                    sensor_avg_change[sensor_id] = []
                    sensor_readings[sensor_id] = []
                
                sensor_press_count[sensor_id] += 1
                sensor_max_change[sensor_id] = max(sensor_max_change[sensor_id], resistance_change)
                sensor_avg_change[sensor_id].append(resistance_change)
                sensor_readings[sensor_id].append(current_resistance)

print(f"\n[OK] Analysis complete! Processed {frames_analyzed} frames")

# Calculate average changes
for sensor_id in sensor_avg_change:
    sensor_avg_change[sensor_id] = np.mean(sensor_avg_change[sensor_id])

# Sort sensors by press count (most frequently pressed first)
sorted_sensors = sorted(sensor_press_count.items(), key=lambda x: x[1], reverse=True)

print(f"\n{'='*80}")
print(f"SENSOR ACTIVATION SUMMARY")
print(f"{'='*80}")
print(f"\nTotal sensors that showed pressure: {len(sensor_press_count)}")
print(f"Total frames analyzed: {frames_analyzed}")

# Display top activated sensors
print(f"\n{'='*80}")
print(f"TOP 50 MOST FREQUENTLY ACTIVATED SENSORS")
print(f"{'='*80}")
print(f"{'Sensor ID':<12} {'Press Count':<15} {'Max Change (Ohms)':<20} {'Avg Change (Ohms)':<20} {'Baseline (Ohms)':<18}")
print(f"{'-'*80}")

top_sensors = sorted_sensors[:50]
for sensor_id, count in top_sensors:
    max_chg = sensor_max_change[sensor_id]
    avg_chg = sensor_avg_change[sensor_id]
    baseline = baseline_dict[sensor_id]
    print(f"{sensor_id:<12} {count:<15} {max_chg:<18.2f} {avg_chg:<18.2f} {baseline:<15.2f}")

# Calculate statistics for all pressed sensors
if sensor_press_count:
    all_press_counts = list(sensor_press_count.values())
    all_max_changes = list(sensor_max_change.values())
    all_avg_changes = list(sensor_avg_change.values())
    
    print(f"\n{'='*80}")
    print(f"STATISTICS FOR ALL ACTIVATED SENSORS")
    print(f"{'='*80}")
    print(f"Press frequency:")
    print(f"  Mean: {np.mean(all_press_counts):.1f} frames")
    print(f"  Median: {np.median(all_press_counts):.1f} frames")
    print(f"  Min: {np.min(all_press_counts)} frames")
    print(f"  Max: {np.max(all_press_counts)} frames")
    
    print(f"\nMaximum resistance change:")
    print(f"  Mean: {np.mean(all_max_changes):.2f} Ohms")
    print(f"  Median: {np.median(all_max_changes):.2f} Ohms")
    print(f"  Min: {np.min(all_max_changes):.2f} Ohms")
    print(f"  Max: {np.max(all_max_changes):.2f} Ohms")
    
    print(f"\nAverage resistance change:")
    print(f"  Mean: {np.mean(all_avg_changes):.2f} Ohms")
    print(f"  Median: {np.median(all_avg_changes):.2f} Ohms")
    print(f"  Min: {np.min(all_avg_changes):.2f} Ohms")
    print(f"  Max: {np.max(all_avg_changes):.2f} Ohms")

# Save detailed results to CSV
output_file = os.path.join(log_folder, "activated_sensors_analysis.csv")
results = []
for sensor_id, count in sorted_sensors:
    results.append({
        'Sensor_ID': sensor_id,
        'Press_Count': count,
        'Max_Resistance_Change_Ohms': sensor_max_change[sensor_id],
        'Avg_Resistance_Change_Ohms': sensor_avg_change[sensor_id],
        'Baseline_Resistance_Ohms': baseline_dict[sensor_id],
        'Max_Resistance_Ohms': max(sensor_readings[sensor_id]),
        'Avg_Resistance_Ohms': np.mean(sensor_readings[sensor_id]),
        'Min_Resistance_Ohms': min(sensor_readings[sensor_id])
    })

results_df = pd.DataFrame(results)
results_df.to_csv(output_file, index=False)
print(f"\n[OK] Detailed results saved to: {output_file}")

# Create a summary of sensor IDs for easy reference
print(f"\n{'='*80}")
print(f"LIST OF ACTIVATED SENSOR IDs (for your experiment)")
print(f"{'='*80}")
print(f"Total activated sensors: {len(sensor_press_count)}")
print(f"\nSensor IDs (sorted by activation frequency):")
sensor_ids = [str(sid) for sid, _ in sorted_sensors]
print(f"[{', '.join(sensor_ids[:100])}")  # Print first 100
if len(sensor_ids) > 100:
    print(f"... and {len(sensor_ids) - 100} more")

# Calculate sensor grid position (assuming 48x48 grid)
rows, cols = 48, 48
print(f"\n{'='*80}")
print(f"SENSOR GRID POSITIONS (Row, Col) FOR TOP ACTIVATED SENSORS")
print(f"{'='*80}")
print(f"{'Sensor ID':<12} {'Row':<8} {'Col':<8} {'Press Count':<15} {'Max Change (Ohms)':<20}")
print(f"{'-'*65}")

for sensor_id, count in sorted_sensors[:30]:
    row = sensor_id // cols
    col = sensor_id % cols
    max_chg = sensor_max_change[sensor_id]
    print(f"{sensor_id:<12} {row:<8} {col:<8} {count:<15} {max_chg:<18.2f}")

print(f"\n{'='*80}")
print(f"ANALYSIS COMPLETE!")
print(f"{'='*80}")

