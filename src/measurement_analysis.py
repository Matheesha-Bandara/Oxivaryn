
import numpy as np
import pandas as pd
from pathlib import Path

# Oxivaryn Measurement Analysis Engine

def calculate_sensor_metrics(time, reference, readings):
    """
    Calculate oxygen sensor performance metrics.

    Parameters:
        time: Measurement times or indices
        reference: Reference oxygen concentrations (%)
        readings: Sensor oxygen concentrations (%)

    Returns:
        Dictionary containing performance metrics.

    Note:
        Drift slope is expressed in percentage points
        per unit of the supplied time axis.
    """

    time = np.asarray(time, dtype=float)
    reference = np.asarray(reference, dtype=float)
    readings = np.asarray(readings, dtype=float)

    # Validate input data
    if time.ndim != 1 or reference.ndim != 1 or readings.ndim != 1:
        raise ValueError("All inputs must be one-dimensional.")

    if not (len(time) == len(reference) == len(readings)):
        raise ValueError("Input arrays must have equal lengths.")

    if len(time) < 3:
        raise ValueError("At least 3 measurements are required.")

    if not all(
        np.all(np.isfinite(arr))
        for arr in (time, reference, readings)
    ):
        raise ValueError("All values must be finite.")

    if np.any(np.diff(time) <= 0):
        raise ValueError("Time values must be strictly increasing.")

    if (
        np.any((reference < 0) | (reference > 100))
        or np.any((readings < 0) | (readings > 100))
    ):
        raise ValueError("Oxygen concentrations must be between 0 and 100%.")

    # Measurement error
    
    error = readings - reference

    # Mean Absolute Error
    
    mae = np.mean(np.abs(error))

    # Mean signed error
    
    bias = np.mean(error)

    # Maximum absolute error
    
    max_error = np.max(np.abs(error))

    # Linear drift estimation
    
    coefficients = np.polyfit(time, error, 1)
    slope = coefficients[0]

    # Remove linear trend
    
    predicted_error = np.polyval(coefficients, time)
    residuals = error - predicted_error

    # Detrended measurement variability
    
    stability = np.std(residuals, ddof=1)

    return {
        "mae": float(mae),
        "bias": float(bias),
        "max_error": float(max_error),
        "slope": float(slope),
        "stability": float(stability)
    }

# Analyze Simulated Sensor Data

def main():

    root = Path(__file__).resolve().parent.parent

    data_path = root / "data" / "oxygen_sensor_data.csv"

    df = pd.read_csv(data_path)

    sensors = ["Healthy", "Drifting", "Degraded"]

    print("\nOxivaryn — Sensor Performance Analysis")
    print("=" * 55)

    for sensor in sensors:

        metrics = calculate_sensor_metrics(
            time=df["Time"],
            reference=df["Reference_Oxygen"],
            readings=df[sensor]
        )

        print(f"\nSensor: {sensor}")

        print(
            f"Mean Absolute Error: "
            f"{metrics['mae']:.3f} pp"
        )

        print(
            f"Mean Bias: "
            f"{metrics['bias']:.3f} pp"
        )

        print(
            f"Maximum Error: "
            f"{metrics['max_error']:.3f} pp"
        )

        print(
            f"Stability (Residual SD): "
            f"{metrics['stability']:.3f} pp"
        )

        print(
            f"Drift Slope: "
            f"{metrics['slope']:.4f} pp/measurement"
        )

    print("\nAnalysis complete.")


if __name__ == "__main__":
    main()
