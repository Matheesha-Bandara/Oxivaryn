
import numpy as np
from measurement_analysis import calculate_sensor_metrics


def check(name, actual, expected):
    passed = np.isclose(actual, expected, atol=1e-8, rtol=0)
    print(f"{'PASS' if passed else 'FAIL'} | {name}")
    return bool(passed)


def main():
    time = np.arange(10, dtype=float)
    reference = np.full(10, 40.0)
    results = []

    print("\nOxivaryn — Analysis Engine Validation")
    print("=" * 45)

    # Test 1: Perfect measurements

    metrics = calculate_sensor_metrics(
        time, reference, reference.copy()
    )

    results.append(check("Perfect MAE", metrics["mae"], 0))
    results.append(check("Perfect bias", metrics["bias"], 0))
    results.append(check("Perfect stability", metrics["stability"], 0))

    # Test 2: Constant offset of -2 pp

    readings = reference - 2.0
    metrics = calculate_sensor_metrics(time, reference, readings)

    results.append(check("Offset MAE", metrics["mae"], 2))
    results.append(check("Offset bias", metrics["bias"], -2))
    results.append(check("Offset maximum error", metrics["max_error"], 2))
    results.append(check("Offset drift", metrics["slope"], 0))

    # Test 3: Linear drift

    readings = reference - 0.1 * time
    metrics = calculate_sensor_metrics(time, reference, readings)

    results.append(check("Linear drift slope", metrics["slope"], -0.1))
    results.append(check("Linear drift MAE", metrics["mae"], 0.45))
    results.append(check("Linear drift stability", metrics["stability"], 0))

    # Test 4: Invalid inputs

    try:
        calculate_sensor_metrics(
            np.array([0, 1, 1]),
            np.array([40, 40, 40]),
            np.array([40, 39, 38])
        )
        results.append(False)
        print("FAIL | Duplicate time rejection")
    except ValueError:
        results.append(True)
        print("PASS | Duplicate time rejection")

    # Final summary
    
    passed = sum(results)
    total = len(results)

    print("\n" + "=" * 45)
    print(f"VALIDATION RESULT: {passed}/{total} PASSED")

    if passed != total:
        raise SystemExit("Validation failed.")

    print("All analysis engine tests passed.")


if __name__ == "__main__":
    main()
