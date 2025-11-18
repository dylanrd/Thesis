import pandas as pd
import os

# Configuration
baseline_file = "100kg/baseline_values.csv"  # Update this path as needed

# Sensor IDs to read
SENSOR_IDS = [492, 534, 539, 585, 632, 639, 676, 678, 683]

def read_baseline_values(sensor_ids, baseline_df):
    """Read baseline values for given sensor IDs"""
    results = []
    for sensor_id in sensor_ids:
        sensor_data = baseline_df[baseline_df['Sensor_ID'] == sensor_id]
        if len(sensor_data) > 0:
            baseline_value = sensor_data.iloc[0]['Baseline_Resistance_Ohms']
            row = sensor_id // 48  # Assuming 48x48 grid
            col = sensor_id % 48
            results.append({
                'Sensor_ID': sensor_id,
                'Row': row,
                'Col': col,
                'Baseline_Resistance_Ohms': baseline_value
            })
        else:
            print(f"Warning: Sensor ID {sensor_id} not found in baseline file")
    
    return results

def main():
    # Check if baseline file exists
    if not os.path.exists(baseline_file):
        print(f"Error: Baseline file not found: {baseline_file}")
        print("Please update the 'baseline_file' path in the script.")
        return
    
    # Load baseline data
    print(f"Loading baseline from: {baseline_file}")
    baseline_df = pd.read_csv(baseline_file)
    print(f"Loaded {len(baseline_df)} sensor baselines")
    
    print("\n" + "="*60)
    print("Baseline Value Reader")
    print("="*60)
    print(f"Reading values for sensor IDs: {SENSOR_IDS}")
    print("="*60 + "\n")
    
    # Read values
    results = read_baseline_values(SENSOR_IDS, baseline_df)
    
    if results:
        print(f"{'Sensor ID':<12} {'Row':<6} {'Col':<6} {'Baseline Resistance (Ohms)':<25}")
        print("-" * 60)
        for result in results:
            print(f"{result['Sensor_ID']:<12} {result['Row']:<6} {result['Col']:<6} {result['Baseline_Resistance_Ohms']:<25.2f}")
        print()
    else:
        print("No valid sensor IDs found\n")

if __name__ == "__main__":
    main()

