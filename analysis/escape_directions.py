import numpy as np
from shapely.geometry import Polygon, LineString, Point
import math
import pandas as pd

# Create Pac-Man shape
def create_pacman(radius=1, mouth_angle_deg=30, segments=100):
    theta = math.radians(mouth_angle_deg / 2)
    arc = [(radius * math.cos(a), radius * math.sin(a))
           for a in np.linspace(theta, 2 * math.pi - theta, segments)]
    return Polygon([(0, 0)] + arc + [(0, 0)])

# Create inner circle to subtract
def create_circle(radius=0.75, segments=100):
    arc = [(radius * math.cos(a), radius * math.sin(a))
           for a in np.linspace(0, 2 * math.pi, segments)]
    return Polygon([(0, 0)] + arc + [(0, 0)])

# Count valid escape directions
def count_escape_directions(c_shape: Polygon, resolution_deg: float = 2.0) -> int:
    center = c_shape.centroid
    count = 0
    for angle_deg in np.arange(0, 360, resolution_deg):
        angle_rad = math.radians(angle_deg)
        ray = LineString([center, (10 * math.cos(angle_rad), 10 * math.sin(angle_rad))])
        if not c_shape.intersects(ray):
            count += 1
    return count


phi_values = np.arange(0, 96, 1)
escape_counts = []

for phi in phi_values:
    pacman = create_pacman(radius=1, mouth_angle_deg=phi)
    inner_circle = create_circle(radius=0.75)
    c_shape = pacman.difference(inner_circle)
    
    valid_count = count_escape_directions(c_shape)
    escape_counts.append((phi, valid_count))

# Save or view as DataFrame
df = pd.DataFrame(escape_counts, columns=["phi", "num_valid_directions"])
print(df)

# Optional: save to CSV
df.to_csv("escape_direction_counts.csv", index=False)
