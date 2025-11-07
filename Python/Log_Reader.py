import matplotlib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import time
from datetime import datetime
from Filters import *
from crosstalk import estimate_cell_conductances_fixed_point

# Configuration
log_file = "two_people/threshold_changes.csv"  # Path to your log file
baseline_file = "two_people/baseline_values.csv"  # Path to baseline file
rows, cols = 48, 48 # Grid dimensions - rows x cols = total sensors
total_sensors = rows * cols  # Total number of sensors (1536 for 48x32)
update_interval = 0.1  # Time interval between heatmaps in seconds
MIN_RESISTANCE_DELTA = 0  # Resistance change threshold (ohms) to ignore

# Performance options
ENABLE_CROSSTALK_CORRECTION = False  # Set to False for faster processing
CROSSTALK_MAX_ITERATIONS = 300  # Reduced from 300 for faster processing
CROSSTALK_TOLERANCE = 1e-4  # Relaxed tolerance for faster convergence

# Filtering strategy selection
FILTERING_STRATEGY = 0  # Choose 0, 1, 2, 3, 4, or 5 to test different approaches (0 = raw values, 5 for testing)
THRESHOLD_VALUE = 0.075  # Adjust this value to control sensitivity (lowered for more detection)
RAW_MODE = False  # Set to True to display raw resistance values without any processing

print(f"📊 Sensor array configuration: {rows} rows × {cols} columns = {total_sensors} sensors")

# Create timestamped output folder
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_folder = f"log_reader_output_{timestamp}"
os.makedirs(output_folder, exist_ok=True)
print(f"📁 Created output folder: {output_folder}")

# Load the data
print("Loading data...")
df = pd.read_csv(log_file)
# Remove duplicate timestamps
df_cleaned = df.drop_duplicates(subset=["Timestamp", "Sensor_ID"], keep="first")
# Group sensor data by timestamp
grouped = df_cleaned.groupby("Timestamp")

# Load baseline data
print("Loading baseline...")
baseline_df = pd.read_csv(baseline_file)
baseline_resistance = baseline_df.sort_values("Sensor_ID")["Baseline_Resistance_Ohms"].values

# Convert baseline to conductance
with np.errstate(divide='ignore', invalid='ignore'):
    baseline_conductance = np.where(baseline_resistance > 0, 1.0 / baseline_resistance, 0.0)

print(f"✅ Baseline loaded: {len(baseline_conductance)} sensors")

# Set matplotlib to non-interactive mode for file-only output
matplotlib.use('Agg')  # Use non-interactive backend

try:
    total_frames = len(grouped)
    print(f"🔄 Processing {total_frames} frames...")
    print(f"⚙️ Mode: {'RAW VALUES (no processing)' if RAW_MODE else 'PROCESSED (with filters/crosstalk)'}")
    if not RAW_MODE:
        print(f"⚙️ Crosstalk correction: {'Enabled' if ENABLE_CROSSTALK_CORRECTION else 'Disabled'}")
    
    for i, (timestamp, group) in enumerate(grouped):
        frame_start_time = time.time()
        
        # Extract and sort sensor values
        current_resistance = group.sort_values("Sensor_ID")["Resistance_Ohms"].values
        resistance_delta = np.abs(current_resistance - baseline_resistance)
        small_change_mask = resistance_delta < MIN_RESISTANCE_DELTA
        adjusted_resistance = current_resistance.copy()
        adjusted_resistance[small_change_mask] = baseline_resistance[small_change_mask]
        
        # Convert to conductance
        with np.errstate(divide='ignore', invalid='ignore'):
            adjusted_conductance = np.where(adjusted_resistance > 0, 1.0 / adjusted_resistance, 0.0)
        
        # Compute pressure difference (positive deltas only) - same as plotter2
        pressure_map = adjusted_conductance - baseline_conductance
        pressure_map = np.clip(pressure_map, 0, None)
        
        # Normalize to [0, 1] for display
        max_val = np.max(pressure_map)
        normalized = pressure_map / max_val if max_val > 0 else pressure_map
        
        sensor_grid = normalized.reshape((rows, cols))
        # Ensure we have the right number of sensors
        if len(current_resistance) < total_sensors:
            # Pad with baseline values for missing sensors
            padded_resistance = np.zeros(total_sensors)
            padded_resistance[:len(current_resistance)] = current_resistance
            padded_resistance[len(current_resistance):] = baseline_resistance[len(current_resistance):]
            current_resistance = padded_resistance
        else:
            current_resistance = current_resistance[:total_sensors]
        
        # RAW MODE: Just display raw resistance values without any processing
        if RAW_MODE:
           
            print(f"  └─ RAW MODE: Displaying raw resistance values")
            print(f"  └─ Range: min={np.min(sensor_grid):.2f}Ω, max={np.max(sensor_grid):.2f}Ω, mean={np.mean(sensor_grid):.2f}Ω")
            
            
            # Plot and save heatmap
            plot_start = time.time()
            fig, ax = plt.subplots()
            heatmap = ax.imshow(sensor_grid, cmap='viridis', vmin=0, vmax=1)
            plt.colorbar(heatmap, label='Normalized Raw Resistance')
            ax.set_title(f'Raw Resistance Map - Frame {i+1} ({timestamp})')
            ax.set_xlabel('Sensor Columns')
            ax.set_ylabel('Sensor Rows')
            plt.savefig(f'{output_folder}/frame_{i:03}.png', bbox_inches='tight', dpi=300)
            plt.close()
            plot_time = time.time() - plot_start
            
            frame_time = time.time() - frame_start_time
            print(f"  └─ Saved frame_{i:03}.png (plot: {plot_time:.1f}s, total: {frame_time:.1f}s)")
            
            # Show progress every 10 frames
            if (i + 1) % 10 == 0:
                avg_time = frame_time
                remaining_frames = total_frames - (i + 1)
                eta = remaining_frames * avg_time
                print(f"📈 Progress: {i+1}/{total_frames} frames ({((i+1)/total_frames)*100:.1f}%) - ETA: {eta/60:.1f} minutes")
            
            continue  # Skip all other processing
        
        # Apply plotter2 logic: suppress small resistance changes
        
        
        # Debug: Check the range of values before any processing
        print(f"  └─ Initial sensor grid range: min={np.min(sensor_grid):.4f}, max={np.max(sensor_grid):.4f}, mean={np.mean(sensor_grid):.4f}")
        
        # Apply thresholding to identify truly pressed pixels FIRST
        pressed_mask = sensor_grid > THRESHOLD_VALUE
        print(f"  └─ Threshold {THRESHOLD_VALUE}: {np.sum(pressed_mask)} pixels above threshold")
        
        # Create a clean grid with only pressed pixels
        sensor_grid_clean = np.where(pressed_mask, sensor_grid, 0)
        
        # Apply filtering strategies FIRST (before crosstalk correction)
        if np.any(pressed_mask):
            print(f"  └─ Found {np.sum(pressed_mask)} pressed pixels, applying strategy {FILTERING_STRATEGY}...")
            
            if FILTERING_STRATEGY == 1:
                # Strategy 1: Multi-peak detection with enhancements (most selective)
                sensor_grid = multi_peak_detection_with_enhancements(sensor_grid_clean, 
                                                                    neighborhood_factor=0.1, 
                                                                    min_peak_fraction=0.2)
                print(f"    Using multi-peak detection (most selective)")
                
            elif FILTERING_STRATEGY == 2:
                # Strategy 2: Adaptive thresholding based on local maxima
                sensor_grid = adaptive_thresholding_max(sensor_grid_clean, threshold_factor=0.7)
                print(f"    Using adaptive thresholding")
                
            elif FILTERING_STRATEGY == 3:
                # Strategy 3: Custom spatial smoothing for pressed regions
                sensor_grid = sensor_grid_clean.copy()
                print(f"    Before spatial smoothing: {np.sum(sensor_grid > 0)} non-zero pixels")
                if np.any(sensor_grid > 0):
                    # Apply light Gaussian filter to smooth the pressed regions
                    sensor_grid = apply_spatial_filter(sensor_grid, sigma=0.5)
                    print(f"    After spatial smoothing: {np.sum(sensor_grid > 0)} non-zero pixels")
                    # Re-threshold to maintain boundaries
                    sensor_grid = np.where(sensor_grid > THRESHOLD_VALUE * 0.3, sensor_grid, 0)
                    print(f"    After re-thresholding: {np.sum(sensor_grid > 0)} non-zero pixels")
                print(f"    Using spatial smoothing")
                
            elif FILTERING_STRATEGY == 4:
                # Strategy 4: Aggressive spatial smoothing for visible results
                sensor_grid = sensor_grid_clean.copy()
                print(f"    Before smoothing: {np.sum(sensor_grid > 0)} non-zero pixels")
                if np.any(sensor_grid > 0):
                    # Apply stronger Gaussian filter for visible smoothing
                    sensor_grid = apply_spatial_filter(sensor_grid, sigma=1.2)
                    print(f"    After Gaussian filter (sigma=1.2): {np.sum(sensor_grid > 0)} non-zero pixels")
                    
                    # Much lower re-threshold to preserve smoothed values
                    sensor_grid = np.where(sensor_grid > THRESHOLD_VALUE * 0.1, sensor_grid, 0)
                    print(f"    After re-thresholding (0.1x): {np.sum(sensor_grid > 0)} non-zero pixels")
                    
                    # Apply a second pass of light smoothing
                    if np.any(sensor_grid > 0):
                        sensor_grid = apply_spatial_filter(sensor_grid, sigma=0.5)
                        print(f"    After second smoothing pass: {np.sum(sensor_grid > 0)} non-zero pixels")
                print(f"    Using aggressive spatial smoothing")
                
            elif FILTERING_STRATEGY == 5:
                # Strategy 5: Simple averaging filter (guaranteed to show changes)
                sensor_grid = sensor_grid_clean.copy()
                print(f"    Before averaging: {np.sum(sensor_grid > 0)} non-zero pixels")
                if np.any(sensor_grid > 0):
                    # Create a simple 3x3 averaging kernel
                    from scipy.ndimage import uniform_filter
                    sensor_grid = uniform_filter(sensor_grid, size=5)
                    print(f"    After 3x3 averaging: {np.sum(sensor_grid > 0)} non-zero pixels")
                    
                    # Very low threshold to preserve smoothed values
                    sensor_grid = np.where(sensor_grid > THRESHOLD_VALUE * 0.05, sensor_grid, 0)
                    print(f"    After re-thresholding (0.05x): {np.sum(sensor_grid > 0)} non-zero pixels")
                print(f"    Using simple averaging filter")
            
            # Re-normalize the filtered result
            max_val = np.max(sensor_grid)
            if max_val > 0:
                sensor_grid = sensor_grid / max_val
                print(f"    After filtering: {np.sum(sensor_grid > 0)} non-zero pixels")
        else:
            print(f"  └─ No pressed pixels detected above threshold {THRESHOLD_VALUE}")
            sensor_grid = sensor_grid_clean
        
        # Apply crosstalk correction AFTER filtering
        if ENABLE_CROSSTALK_CORRECTION:
            crosstalk_start = time.time()
            print(f"  └─ Applying crosstalk correction to filtered data...", end="", flush=True)
            sensor_grid = estimate_cell_conductances_fixed_point(
                sensor_grid, 
                max_iterations=CROSSTALK_MAX_ITERATIONS,
                tolerance=CROSSTALK_TOLERANCE
            )
            crosstalk_time = time.time() - crosstalk_start
            # print(f" Done ({crosstalk_time:.1f}s)")
            # from scipy.ndimage import uniform_filter
            # sensor_grid = uniform_filter(sensor_grid, size=10)
            # print(f"    After 3x3 averaging: {np.sum(sensor_grid > 0)} non-zero pixels")
            
            # # Very low threshold to preserve smoothed values
            # sensor_grid = np.where(sensor_grid > THRESHOLD_VALUE * 0.05, sensor_grid, 0)

            # # Re-normalize after crosstalk correction to enhance contrast
            max_val = np.max(sensor_grid)
            if max_val > 0:
                # Use a more aggressive normalization to make corrected values stand out
                sensor_grid = np.power(sensor_grid / max_val, 0.7)  # Gamma correction for better contrast
                print(f"    After crosstalk correction: {np.sum(sensor_grid > 0)} non-zero pixels")
        else:
            print(f"  └─ Skipping crosstalk correction")
        
        # Plot and save heatmap
        plot_start = time.time()
        fig, ax = plt.subplots()
        heatmap = ax.imshow(sensor_grid, cmap='plasma', vmin=0, vmax=1)
        plt.colorbar(heatmap, label='Normalized Pressure')
        ax.set_title(f'Pressure Map - Frame {i+1} ({timestamp})')
        ax.set_xlabel('Sensor Columns')
        ax.set_ylabel('Sensor Rows')
        plt.savefig(f'{output_folder}/frame_{i:03}.png', bbox_inches='tight', dpi=300)
        plt.close()
        plot_time = time.time() - plot_start
        
        frame_time = time.time() - frame_start_time
        print(f"  └─ Saved frame_{i:03}.png (plot: {plot_time:.1f}s, total: {frame_time:.1f}s)")
        
        # Show progress every 10 frames
        if (i + 1) % 10 == 0:
            avg_time = frame_time
            remaining_frames = total_frames - (i + 1)
            eta = remaining_frames * avg_time
            print(f"📈 Progress: {i+1}/{total_frames} frames ({((i+1)/total_frames)*100:.1f}%) - ETA: {eta/60:.1f} minutes")

    print(f"✅ Finished processing all heatmaps.")
    print(f"📁 All frames saved to: {output_folder}/")

except KeyboardInterrupt:
    print("Stopped by user.")
finally:
    plt.close('all')  # Close any remaining figures
