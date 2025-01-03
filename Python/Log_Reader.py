import matplotlib
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from Filters import *
# matplotlib.use('TkAgg')
# Configuration
log_file = "sensor_readings.csv"  # Path to your log file
rows, cols = 16, 15  # Grid dimensions (e.g., 80x100 for 8000 sensors)
update_interval = 0.1  # Time interval between heatmaps in seconds

# Load the data
print("Loading data...")
df = pd.read_csv(log_file)
# Remove duplicate timestamps
df_cleaned = df.drop_duplicates(subset=["Timestamp", "Sensor_ID"], keep="first")
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
    for timestamp, group in grouped:

        # Extract sensor values and reshape into a 2D grid
        sensor_values = group.sort_values("Sensor_ID")["Resistance"].values

        sensor_values = 1/sensor_values
        sensor_grid = sensor_values.reshape((cols, rows))
        print(sensor_grid)

        # ax.clear()
        #
        # # Recreate the heatmap with the updated data
        # heatmap = sns.heatmap(sensor_grid, ax=ax, cbar=False)
        #
        # # Reuse the colorbar from the previous heatmap
        # colorbar = heatmap.collections[0].colorbar
        #
        # # Update colorbar limits to match the data range
        # # colorbar.set_ticks(np.linspace(sensor_grid.min(), sensor_grid.max(), 5))
        #
        # # Set the title of the heatmap
        # ax.set_title(f"Sensor Heatmap at {timestamp}")

        # heatmap.set_data(apply_spatial_filter(weighted_neighbor_correction(adaptive_thresholding_max(1/sensor_grid))))
        # heatmap.set_data(sensor_grid)
        # plt.colorbar(heatmap)
        fig, ax = plt.subplots()
        heatmap = ax.imshow((sensor_grid))
        plt.colorbar(heatmap)
        plt.show()
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
