import matplotlib
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from Filters import *
from crosstalk import estimate_cell_conductances_fixed_point
# matplotlib.use('TkAgg')
# Configuration
log_file = "sensor_readings4.csv"  # Path to your log file
rows, cols = 16, 15  # Grid dimensions (e.g., 80x100 for 8000 sensors)
update_interval = 0.1  # Time interval between heatmaps in seconds

# Load the data
print("Loading data...")
df = pd.read_csv(log_file)
# Remove duplicate timestamps
df_cleaned = df.drop_duplicates(subset=["Timestamp", "Sensor ID"], keep="first")
# Group sensor data by timestamp
grouped = df_cleaned.groupby("Timestamp")

# Initialize the plot
plt.ion()  # Enable interactive mode
fig, ax = plt.subplots()
# heatmap = ax.imshow(np.zeros((15, 16)))

initial_data = np.zeros((rows, cols))
heatmap = sns.heatmap(initial_data, ax=ax, cbar=True)

# Access the colorbar from the heatmap
colorbar = heatmap.collections[0].colorbar

# max = grouped[0][1].sort_values("Sensor_ID")["Resistance"].values.reshape((cols, rows))
try:
    # Loop through each timestamp
    for i, (timestamp, group) in enumerate(grouped):

        # Extract sensor values and reshape into a 2D grid
        sensor_values = group.sort_values("Sensor ID")["Resistance (Ohms)"].values

        sensor_values = 1/sensor_values
        pad = 240 - len(sensor_values)
        sensor_grid = np.pad(sensor_values, (0, pad), mode='constant', constant_values=1)
        sensor_grid = sensor_grid.reshape((cols, rows))
        sensor_grid = estimate_cell_conductances_fixed_point(sensor_grid)
        fig, ax = plt.subplots()
        heatmap = ax.imshow((sensor_grid))
        plt.colorbar(heatmap)
        # plt.show()
        plt.savefig(f'unfiltered/frame_0{i}.png', bbox_inches='tight', dpi=300)
        plt.close()
        # Clear and update the heatmap
        # ax.clear()
        # sns.heatmap(sensor_grid, ax=ax, cbar=True)
        # ax.set_title(f"Sensor Heatmap at {timestamp}")

        # Show the updated heatmap
        # plt.pause(update_interval)  # Pause for the interval to show the frame

    print("Finished displaying all heatmaps.")

except KeyboardInterrupt:
    print("Stopped by user.")
finally:
    plt.ioff()
    plt.show()
