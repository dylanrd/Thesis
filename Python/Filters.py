import numpy as np
from scipy.ndimage import median_filter
from scipy.signal import savgol_filter
from scipy.ndimage import gaussian_filter

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

def adaptive_thresholding(matrix, threshold_factor=1.5):
    """ Apply an adaptive threshold to each sensor based on the row average. """
    corrected_matrix = np.zeros_like(matrix)
    for i, row in enumerate(matrix):
        mean_row = np.mean(row)
        for j, value in enumerate(row):
            if value > threshold_factor * mean_row:
                corrected_matrix[i, j] = value
    return corrected_matrix


def weighted_neighbor_correction(matrix, weight=0.5):
    """ Adjust sensor readings based on neighboring sensors. """
    corrected_matrix = np.copy(matrix)
    n_rows, n_cols = matrix.shape

    for i in range(1, n_rows - 1):
        for j in range(1, n_cols - 1):
            # Average value of the 4 neighboring sensors (up, down, left, right)
            neighbors = [matrix[i-1, j], matrix[i+1, j], matrix[i, j-1], matrix[i, j+1]]
            neighbor_avg = np.mean(neighbors)
            if matrix[i, j] > neighbor_avg * 1.5:
                corrected_matrix[i, j] = (1 - weight) * matrix[i, j] + weight * neighbor_avg
    return corrected_matrix





### 4. Spatial Filtering (Gaussian Filter) ###
def apply_spatial_filter(matrix, sigma=1.0):
    """ Apply a Gaussian filter to smooth the matrix. """
    return gaussian_filter(matrix, sigma=sigma)

