import numpy as np
import scipy.linalg
import matplotlib.pyplot as plt
def create_conductance_matrix(g):
    """
    Creates the conductance matrix C for the linear system of equations.

    Args:
        g (numpy.ndarray): A 2D numpy array representing the cell conductances (g_ji).

    Returns:
        numpy.ndarray: The conductance matrix C.
    """
    N, M = g.shape  # N = number of rows, M = number of columns
    C = np.zeros((N + M - 1, N + M - 1))

    # Calculate row and column sums of conductances
    row_sums = np.sum(g, axis=1)
    col_sums = np.sum(g, axis=0)

    # Fill in the matrix elements
    for i in range(1, N):  # Rows 2 to N (index 0 is row 1 which is the reference)
        C[i - 1, i - 1] = row_sums[i]  # Diagonal elements for rows
        for j in range(M):
            C[i - 1, N - 1 + j] = -g[i, j]  # Off-diagonal elements for rows

    for j in range(M):  # Columns
        C[N - 1 + j, N - 1 + j] = col_sums[j]  # Diagonal elements for columns
        for i in range(1, N):
            C[N - 1 + j, i - 1] = -g[i, j]  # Off-diagonal elements for columns

    return C


def calculate_equivalent_conductance(g, i, j):
    """
    Calculates the equivalent conductance G_ji between row i and column j
    given the cell conductances g.

    Args:
        g (numpy.ndarray): A 2D numpy array representing the cell conductances (g_ji).
        i (int): The row index (starting from 1).
        j (int): The column index (starting from 0).

    Returns:
        float: The equivalent conductance G_ji.
    """
    N, M = g.shape
    C = create_conductance_matrix(g)
    Iref = 1.0  # Reference current

    # Create the current vector I
    I = np.zeros(N + M - 1)
    if i > 1:
        I[i - 2] = -Iref  # Row current injection
    I[N - 1 + j] = Iref  # Column current extraction

    # Solve the linear system CV = I
    V = scipy.linalg.solve(C, I)

    # Calculate the voltage difference
    if i > 1:
        V_i = V[i - 2]  # Voltage at row i
    else:
        V_i = 0.0  # Row 1 is the reference (ground)

    V_j = V[N - 1 + j]  # Voltage at column j

    # Calculate the equivalent conductance
    G_ji = Iref / (V_j - V_i)
    return G_ji


def estimate_cell_conductances_fixed_point(G, initial_guess=None, max_iterations=150, tolerance=1e-6, relaxation_factor=0.5):
    """
    Estimates the cell conductances g_ji from the equivalent conductances G_ji
    using a fixed-point iteration method.

    Args:
        G (numpy.ndarray): A 2D numpy array representing the measured equivalent conductances (G_ji).
        initial_guess (numpy.ndarray, optional): An initial guess for the cell conductances (g_ji).
                                                  If None, a default initial guess is used. Defaults to None.
        max_iterations (int, optional): The maximum number of iterations. Defaults to 100.
        tolerance (float, optional): The convergence tolerance. Defaults to 1e-6.
        relaxation_factor (float, optional): The relaxation factor to improve convergence. Defaults to 0.5.

    Returns:
        numpy.ndarray: The estimated cell conductances (g_ji).
    """
    N, M = G.shape  #N rows and M columns

    # Initialize cell conductances
    if initial_guess is None:
        g_est = np.ones((N, M))  # Start with all conductances equal to 1
    else:
        g_est = initial_guess.copy() #use the copy to avoid modifying the input data

    for iteration in range(max_iterations):
        g_est_prev = g_est.copy()

        # Iterate over all cells
        for i in range(N):
            for j in range(M):
                # Calculate equivalent conductance using current estimate
                G_est_ji = calculate_equivalent_conductance(g_est, i + 1, j)

                # Update cell conductance using fixed-point iteration with relaxation
                g_est[i, j] = g_est_prev[i, j] + relaxation_factor * (G[i, j] - G_est_ji)

                # Ensure non-negative conductance
                g_est[i, j] = max(0.0, g_est[i, j])

        # Check for convergence
        change = np.sum(np.abs(g_est - g_est_prev))
        if change < tolerance:
            print(f"Fixed-point iteration converged after {iteration + 1} iterations")
            return g_est

    print("Fixed-point iteration did not converge within the maximum number of iterations")
    return g_est


# Example Usage:
if __name__ == '__main__':
    # Define the size of the sensor array
    N = 3  # Number of rows
    M = 3  # Number of columns

    # Create a sample cell conductance matrix (replace with your actual values)
    g_true = np.random.rand(N, M)  # Random conductances between 0 and 1
    print("True cell conductances:\n", g_true)

    # Calculate the equivalent conductance matrix G
    G = np.zeros((N, M))
    for i in range(N):
        for j in range(M):
            G[i, j] = calculate_equivalent_conductance(g_true, i + 1, j)
    print("\nEquivalent conductances:\n", G)

    # Estimate cell conductances from equivalent conductances using fixed-point iteration
    g_estimated = estimate_cell_conductances_fixed_point(G)
    print("\nEstimated cell conductances:\n", g_estimated)

    # Calculate the relative error
    relative_error = np.mean(np.abs((g_estimated - g_true) / g_true))
    print(f"\nMean relative error: {relative_error:.4f}")

    g_estimated = (g_estimated - np.min(g_estimated)) / (np.max(g_estimated) - np.min(g_estimated) + 1e-9)

    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.imshow(G, cmap='viridis', interpolation='nearest')
    plt.colorbar(label='Measured Conductance (S)')
    plt.title('Measured Conductances')

    plt.subplot(1, 2, 2)
    plt.imshow(g_estimated, cmap='viridis', interpolation='nearest')
    plt.colorbar(label='Estimated True Conductance (Normalized)')
    plt.title('Estimated True Conductances')

    plt.tight_layout()
    plt.show()

