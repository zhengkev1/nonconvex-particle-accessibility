import numpy as np
import matplotlib.pyplot as plt

# Data (Height, Accessibility, Change_of_Height)
data = [
    (1.00, 0.88158, 0.016),
    (0.75, 0.92284, 0.021),
    (1.20, 0.86779, 0.012),
    (0.50, 0.94228, 0.023),
    (1.10, 0.87537, 0.015),
    (0.90, 0.89166, 0.0165)
]

# Extract Accessibility (y) and Change_of_Height (x)
x = np.array([row[2] for row in data])   # Change of Height
y = np.array([row[1] for row in data])   # Accessibility

# Sort by x for smoother plotting
order = np.argsort(x)
x = x[order]
y = y[order]

# Define sigmoid function
def sigmoid(x, a, b):
    return 1 / (1 + np.exp(-(a * x + b)))

# Fit sigmoid using linear regression on logit(y)
eps = 1e-6
y_clip = np.clip(y, eps, 1 - eps)
logit_y = np.log(y_clip / (1 - y_clip))
A = np.vstack([x, np.ones_like(x)]).T
a, b = np.linalg.lstsq(A, logit_y, rcond=None)[0]

# Generate smooth curve
x_grid = np.linspace(x.min(), x.max(), 200)
y_fit = sigmoid(x_grid, a, b)

# Plot
plt.figure(figsize=(7,5))
plt.scatter(x, y, color="blue", s=80, label="Data points")
plt.plot(x_grid, y_fit, color="red", linewidth=2, label="Sigmoid fit")
plt.xlabel("Change of Height")
plt.ylabel("Accessibility")
plt.title("Accessibility vs Change of Height (Sigmoid Fit)")
plt.legend()
plt.grid(True)
plt.savefig("figures/accessibility_vs_height_change.png", dpi=200, bbox_inches="tight")
print(f"sigmoid fit: a = {a:.2f}, b = {b:.3f}")
plt.show()
