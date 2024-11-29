import numpy as np
from scipy.linalg import solve

# Function to compute equivalent conductances
def compute_equivalent_conductance(conductances):
    n, m = conductances.shape
    equivalent_conductances = np.zeros((n, m))

    for i in range(n):
        for j in range(m):
            G = np.zeros(n + m - 1)
            G[i] = -1
            G[n - 1 + j] = 1

            # Conductance matrix setup with added regularization
            C = np.zeros((n + m - 1, n + m - 1))
            for k in range(n):
                for l in range(m):
                    C[k, k] += conductances[k, l]
                    if k != i:
                        C[k, n - 1 + l] = -conductances[k, l]
            for l in range(m):
                for k in range(n):
                    C[n - 1 + l, n - 1 + l] += conductances[k, l]
                    if l != j:
                        C[n - 1 + l, k] = -conductances[k, l]

            C += np.eye(n + m - 1) * 1e-6  # Increase regularization

            # Solve for voltages
            try:
                voltages = solve(C, G)
                voltage_difference = voltages[j] - voltages[i]
                equivalent_conductances[i, j] = 1 / (voltage_difference + 1e-6)  # Avoid division by zero
            except np.linalg.LinAlgError:
                equivalent_conductances[i, j] = 1e10  # Assign a large finite value if the matrix is singular

    return equivalent_conductances

# Fixed-Point Iteration function with checks
def fixed_point_recover_conductances(measured_equivalent_conductances, max_iter=100, tol=1e-6, beta=0.5):
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

# Simulate and recover a 16x16 matrix
# np.random.seed(0)
# true_conductances = np.random.uniform(0.1, 1.0, size=(16, 15))
# measured_equivalent_conductances = compute_equivalent_conductance(true_conductances)
# recovered_conductances, final_error = fixed_point_recover_conductances(measured_equivalent_conductances)

# Output results
# print("Final Error after Correction:", final_error)
