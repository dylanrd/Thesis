import numpy as np
from scipy.linalg import solve

# Function to compute equivalent conductances for a given NxN conductance matrix
def compute_equivalent_conductance(conductances):
    """Compute equivalent conductances for a given NxN conductance matrix."""
    n, m = conductances.shape
    equivalent_conductances = np.zeros((n, m))

    for i in range(n):
        for j in range(m):
            G = np.zeros(n + m)  # Extend to handle both row and column nodes explicitly
            G[i] = -1  # Inject current at row i
            G[n + j] = 1  # Extract current at column j

            # Create the conductance matrix for Kirchhoff's Law
            C = np.zeros((n + m, n + m))

            # Fill in the conductance matrix
            for k in range(n):
                for l in range(m):
                    C[k, k] += conductances[k, l]  # Row contributions
                    C[n + l, n + l] += conductances[k, l]  # Column contributions
                    C[k, n + l] -= conductances[k, l]
                    C[n + l, k] -= conductances[k, l]

            # Regularize and solve the system
            C[n + m - 1, n + m - 1] += 1e-6  # Small regularization on one node
            try:
                voltages = solve(C, G)
                voltage_difference = voltages[n + j] - voltages[i]
                equivalent_conductances[i, j] = 1 / (voltage_difference + 1e-6)  # Avoid division by zero
            except np.linalg.LinAlgError:
                equivalent_conductances[i, j] = 1e10  # Fallback for singular matrix

    return equivalent_conductances


# Fixed-Point Iteration function with checks
def fixed_point_recover_conductances(measured_equivalent_conductances, max_iter=100, tol=1e-6, beta=0.5):
    """Recover conductances using Fixed-Point Iteration."""
    n, m = measured_equivalent_conductances.shape
    g_recovered = np.maximum(measured_equivalent_conductances, 1e-6)  # Ensure no conductance is zero

    for _ in range(max_iter):
        G_estimated = compute_equivalent_conductance(g_recovered)
        error = np.max(np.abs(G_estimated - measured_equivalent_conductances))

        if error < tol:
            break

        g_recovered += beta * (measured_equivalent_conductances - G_estimated)
        g_recovered = np.maximum(g_recovered, 1e-6)  # Ensure no conductance is zero

    return g_recovered, error

#
# # Simulate a 16x16 matrix of true conductances
# np.random.seed(0)
# true_conductances = np.random.uniform(0.1, 1.0, size=(16, 16))
#
# # Compute the "measured" equivalent conductances (affected by crosstalk)
# measured_equivalent_conductances = compute_equivalent_conductance(true_conductances)
#
# # Recover the true conductances using Fixed-Point Iteration
# recovered_conductances, final_error = fixed_point_recover_conductances(measured_equivalent_conductances)
#
# # Output results
# print("True Conductances (First 5 Rows):\n", true_conductances[:5, :5])
# print("Measured Conductances (First 5 Rows):\n", measured_equivalent_conductances[:5, :5])
# print("Recovered Conductances (First 5 Rows):\n", recovered_conductances[:5, :5])
# print(f"Final Error after Correction: {final_error:.6f}")
