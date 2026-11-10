
import pandas as pd
import numpy as np

DATASET = "sentinel_x_validated_dataset.csv"
PREDICTIONS = "sentinel_x_model_predictions.csv"

df = pd.read_csv(DATASET)
pred = pd.read_csv(PREDICTIONS)

print("SENTINEL-X MODEL DIAGNOSTICS")
print("-" * 45)

# 1. Check dataset distribution
print("\nREADINGS PER TAG AND DISTANCE")

counts = pd.crosstab(
    df["Tag_ID"],
    df["Distance_m"]
)

print(counts.to_string())

# 2. Check readings per session
print("\nREADINGS PER SESSION")

print(
    df.groupby("Session_ID").size().to_string()
)

# 3. Average RSSI at each distance for each tag
print("\nMEAN RSSI PER TAG AND DISTANCE")

means = df.pivot_table(
    index="Distance_m",
    columns="Tag_ID",
    values="RSSI_dBm",
    aggfunc="mean"
)

print(means.round(2).to_string())

# 4. Check prediction errors
pred["Error_m"] = (
    pred["Predicted_Distance_m"]
    - pred["Actual_Distance_m"]
)

print("\nPREDICTION RESULTS")

print(
    pred.groupby("Actual_Distance_m").agg(
        Number_of_Predictions=("Error_m", "count"),
        Mean_Error=("Error_m", "mean"),
        Mean_Absolute_Error=(
            "Absolute_Error_m", "mean"
        )
    ).round(3).to_string()
)

print("\nACTUAL VS PREDICTED DISTANCES")

print(pred.round(3).to_string(index=False))

print("\nDIAGNOSTICS COMPLETED")
