import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file
df = pd.read_csv("results/c_shape_vs_mouth_angle.csv")

# Plot
plt.figure(figsize=(10, 6))
plt.plot(df["escape_fraction"], df["accessibility"], marker='o', linestyle='-')
plt.xlabel("Angle Possibility")
plt.ylabel("Accessibility")
plt.title("Accessibility vs Angle Possibility")
plt.grid(True)
plt.savefig("figures/accessibility_vs_escape_fraction.png", dpi=300)  # You can change to .pdf, .svg, etc.

plt.tight_layout()
plt.show()
