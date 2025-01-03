import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import time

# Configuration
log_file = "sensor_readings.csv"  # Path to your log file
rows, cols = 80, 100  # Grid dimensions (e.g., 80x100 for 8000 sensors)
data_shape = (rows, cols)
update_interval = 0.1  # Time interval between frames in seconds

# Load the data
print("Loading data...")
df = pd.read_csv(log_file)

# Extract timestamps and sensor data
timestamps = df['Timestamp']
sensor_data = df.iloc[:, 1:].astype(float).values  # Exclude 'Timestamp' column

# Initialize the heatmap
plt.ion()  # Enable interactive mode
fig, ax = plt.subplots(figsize=(10, 8))

# Loop through all rows to simulate a live display
try:
    for i, row in enumerate(sensor_data):
        # Reshape the sensor data into a 2D grid
        sensor_grid = row.reshape(data_shape)

        # Update the heatmap
        ax.clear()  # Clear previous frame
        sns.heatmap(sensor_grid, ax=ax, cmap="coolwarm", cbar=True)
        ax.set_title(f"Sensor Heatmap at {timestamps[i]}")

        # Display the heatmap
        plt.pause(update_interval)  # Pause for the update interval

    print("Completed displaying all timestamps.")

except KeyboardInterrupt:
    print("Visualization interrupted by user.")
finally:
    plt.ioff()
    plt.show()
