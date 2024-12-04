import numpy as np
from scipy.ndimage import median_filter
from scipy.signal import savgol_filter


def moving_average_filter(matrix, window_size=3):
    filtered_matrix = []
    for row in matrix:
        # Apply moving average filter to each row (sensor data over time)
        filtered_row = np.convolve(row, np.ones(window_size) / window_size, mode='valid')
        filtered_matrix.append(filtered_row)
    return np.array(filtered_matrix)


def exponential_moving_average(matrix, alpha=0.2):
    filtered_matrix = []
    for row in matrix:
        ema_row = [row[0]]  # Initialize with the first data point
        for i in range(1, len(row)):
            ema_row.append(alpha * row[i] + (1 - alpha) * ema_row[-1])
        filtered_matrix.append(ema_row)
    return np.array(filtered_matrix)


def apply_median_filter(matrix, window_size=3):
    # Apply a median filter along the time axis (axis=1)
    filtered_matrix = median_filter(matrix, size=(1, window_size))
    return filtered_matrix


def apply_savitzky_golay_filter(matrix, window_length=3, polyorder=2):
    filtered_matrix = []
    for row in matrix:
        filtered_row = savgol_filter(row, window_length=window_length, polyorder=polyorder)
        filtered_matrix.append(filtered_row)
    return np.array(filtered_matrix)
