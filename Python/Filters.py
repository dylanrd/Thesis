import numpy as np
from scipy.ndimage import median_filter
from scipy.signal import savgol_filter
from scipy.ndimage import gaussian_filter
from scipy.ndimage import maximum_filter
from sklearn.cluster import DBSCAN
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


def compensate_row_and_column_minimum(sensor_matrix):
    """
    Compensate each row and column of the matrix by subtracting the minimum values.

    Parameters:
        sensor_matrix (numpy array): Input matrix of sensor readings.

    Returns:
        numpy array: Matrix after row and column compensation.
    """
    # Step 1: Row-wise minimum compensation
    row_compensated_matrix = np.zeros_like(sensor_matrix)
    for i, row in enumerate(sensor_matrix):
        row_min = np.min(row)  # Find the minimum value in the row
        row_compensated_matrix[i] = row - row_min  # Subtract it from the row
        row_compensated_matrix[i][row_compensated_matrix[i] < 0] = 0  # Ensure non-negative values

    # Step 2: Column-wise minimum compensation
    col_compensated_matrix = np.zeros_like(row_compensated_matrix)
    for j in range(row_compensated_matrix.shape[1]):
        col_min = np.min(row_compensated_matrix[:, j])  # Find the minimum value in the column
        col_compensated_matrix[:, j] = row_compensated_matrix[:, j] - col_min  # Subtract it from the column
        col_compensated_matrix[col_compensated_matrix[:, j] < 0, j] = 0  # Ensure non-negative values

    return col_compensated_matrix

def multi_peak_detection_with_enhancements(sensor_matrix, neighborhood_factor=0.2, min_peak_fraction=0.2, min_cluster_size=1):
    """
    Detect multiple significant peaks with crosstalk suppression, adaptive thresholding, and clustering.

    Parameters:
        sensor_matrix (numpy array): Input matrix of sensor readings.
        neighborhood_factor (float): Fraction of matrix size to determine neighborhood size.
        min_peak_fraction (float): Fraction of maximum value per row/column to set as a threshold.
        min_cluster_size (int): Minimum size of clusters to retain.

    Returns:
        numpy array: Matrix with clustered peaks retained and crosstalk suppressed.
    """
    # Step 1: Compute adaptive threshold per row and column based on their mean or max
    row_thresholds = np.max(sensor_matrix, axis=1) * min_peak_fraction
    col_thresholds = np.max(sensor_matrix, axis=0) * min_peak_fraction

    # Apply row and column adaptive thresholds
    thresholded_matrix = np.zeros_like(sensor_matrix)
    for i in range(sensor_matrix.shape[0]):
        for j in range(sensor_matrix.shape[1]):
            if sensor_matrix[i, j] >= row_thresholds[i] and sensor_matrix[i, j] >= col_thresholds[j]:
                thresholded_matrix[i, j] = sensor_matrix[i, j]

    # Step 2: Detect local maxima with adaptive neighborhood size
    neighborhood_size = int(max(1, neighborhood_factor * max(sensor_matrix.shape)))  # Adaptive neighborhood
    local_max = (thresholded_matrix == maximum_filter(thresholded_matrix, size=neighborhood_size))

    # Retain only the peaks
    peaks = np.where(local_max & (thresholded_matrix > 0), thresholded_matrix, 0)

    # Step 3: Clustering to group adjacent peaks (DBSCAN clustering)
    # Create a list of (row, col) positions of detected peaks
    peak_positions = np.array(np.nonzero(peaks)).T  # Get indices of non-zero peaks

    if len(peak_positions) > 0:
        clustering = DBSCAN(eps=neighborhood_size, min_samples=min_cluster_size).fit(peak_positions)

        # Create a matrix for clustered peaks
        clustered_peaks = np.zeros_like(sensor_matrix)
        for cluster_id in np.unique(clustering.labels_):
            if cluster_id != -1:  # Exclude noise points
                cluster_indices = peak_positions[clustering.labels_ == cluster_id]
                # Retain maximum value in the cluster
                max_value = np.max([sensor_matrix[row, col] for row, col in cluster_indices])
                for row, col in cluster_indices:
                    clustered_peaks[row, col] = max_value

        return clustered_peaks

    return peaks  # If no clusters are found, return peaks