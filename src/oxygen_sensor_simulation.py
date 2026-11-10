import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Set a fixed random seed for repeatable results

np.random.seed(42)

# Simulate 100 measurements

time = np.arange(100)

# Verified reference oxygen concentration (simulated)

reference = np.full(100, 40.0)

# Simulated sensor conditions

healthy = reference + np.random.normal(0, 0.2, 100)

drifting = (
    reference
    + np.linspace(0, -4, 100)
    + np.random.normal(0, 0.2, 100)
)

degraded = (
    reference
    + np.linspace(0, -10, 100)
    + np.random.normal(0, 0.8, 100)
)

# Create dataset

df = pd.DataFrame({
    "Time": time,
    "Reference_Oxygen": reference,
    "Healthy": healthy,
    "Drifting": drifting,
    "Degraded": degraded
})

# Locate the project folder

root = Path(__file__).resolve().parent.parent
data_dir = root / "data"
data_dir.mkdir(exist_ok=True)

# Save measurements

df.to_csv(data_dir / "oxygen_sensor_data.csv", index=False)

# Plot the results

plt.figure(figsize=(10, 5))

plt.plot(time, reference, "--", label="Reference (40%)")
plt.plot(time, healthy, label="Healthy")
plt.plot(time, drifting, label="Drifting")
plt.plot(time, degraded, label="Degraded")

plt.title("Oxivaryn — Simulated Oxygen Sensor Measurements")
plt.xlabel("Measurement Number")
plt.ylabel("Oxygen Concentration (%)")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()

print("Dataset successfully saved!")
print(df.head())
