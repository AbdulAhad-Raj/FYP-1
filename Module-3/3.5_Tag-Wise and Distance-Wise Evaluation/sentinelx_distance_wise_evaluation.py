
import pandas as pd
import numpy as np

print("SENTINEL-X")
print("DISTANCE-WISE MODEL EVALUATION")
print("-" * 55)

# Load the complete prediction file
df = pd.read_csv("sentinel_x_model_predictions.csv")

# Check required columns
required = [
    "Tag_ID",
    "Actual_Distance_m",
    "Predicted_Distance_m"
]

for column in required:
    if column not in df.columns:
        raise ValueError(f"Missing required column: {column}")

# Calculate absolute and squared errors
df["Absolute_Error_m"] = (
    df["Actual_Distance_m"] -
    df["Predicted_Distance_m"]
).abs()

df["Squared_Error"] = (
    df["Actual_Distance_m"] -
    df["Predicted_Distance_m"]
) ** 2

# Calculate distance-wise performance
results = []

for distance, group in df.groupby("Actual_Distance_m"):

    mae = group["Absolute_Error_m"].mean()

    rmse = np.sqrt(group["Squared_Error"].mean())

    within_05 = (
        group["Absolute_Error_m"] <= 0.5
    ).mean() * 100

    within_1 = (
        group["Absolute_Error_m"] <= 1.0
    ).mean() * 100

    results.append({
        "Actual_Distance_m": distance,
        "Readings": len(group),
        "MAE_m": round(mae, 3),
        "RMSE_m": round(rmse, 3),
        "Within_0.5m_%": round(within_05, 2),
        "Within_1m_%": round(within_1, 2)
    })

summary = pd.DataFrame(results)

print("\nDISTANCE-WISE PERFORMANCE")
print(summary.to_string(index=False))

# Evaluate individual tags at each distance
tag_results = df.groupby(
    ["Actual_Distance_m", "Tag_ID"]
).agg(
    Readings=("Absolute_Error_m", "count"),
    MAE_m=("Absolute_Error_m", "mean"),
    RMSE_m=("Squared_Error",
            lambda x: np.sqrt(x.mean()))
).reset_index()

tag_results["MAE_m"] = tag_results["MAE_m"].round(3)
tag_results["RMSE_m"] = tag_results["RMSE_m"].round(3)

print("\nTAG-WISE PERFORMANCE AT EACH DISTANCE")
print(tag_results.to_string(index=False))

# Save evaluation reports
summary.to_csv(
    "sentinelx_distance_wise_summary.csv",
    index=False
)

tag_results.to_csv(
    "sentinelx_tag_distance_evaluation.csv",
    index=False
)

print("\nEvaluation completed successfully.")
print("Generated:")
print("1. sentinelx_distance_wise_summary.csv")
print("2. sentinelx_tag_distance_evaluation.csv")
