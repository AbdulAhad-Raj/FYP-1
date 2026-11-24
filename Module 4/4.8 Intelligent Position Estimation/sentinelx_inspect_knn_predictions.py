
import pandas as pd
import numpy as np

FILE = "06_knn_position_estimation_results.csv"

df = pd.read_csv(FILE)

print("=" * 65)
print("SENTINEL-X KNN PREDICTION INSPECTION")
print("=" * 65)

# 1. Basic information
print("\n1. PREDICTION DATASET")
print("Total test predictions:", len(df))
print("Missing values:")
print(df.isnull().sum())

# 2. Compare actual and predicted coordinates
print("\n2. ACTUAL VS PREDICTED COORDINATES")

columns = [
    "Ground_Truth_Position",
    "Actual_X_m",
    "Actual_Y_m",
    "Predicted_X_m",
    "Predicted_Y_m",
    "Radial_Error_m"
]

print(df[columns].to_string(index=False))

# 3. Unique predicted coordinates
print("\n3. UNIQUE PREDICTED COORDINATES")

unique_predictions = df[
    ["Predicted_X_m", "Predicted_Y_m"]
].drop_duplicates()

print(unique_predictions.to_string(index=False))

# 4. Position-wise prediction accuracy
print("\n4. ERROR BY POSITION")

summary = df.groupby("Ground_Truth_Position").agg(
    Test_Count=("Radial_Error_m", "count"),
    Mean_Error=("Radial_Error_m", "mean"),
    Maximum_Error=("Radial_Error_m", "max")
)

print(summary)

# 5. Check whether predictions are only the five known points
known_coordinates = {
    "CENTRE": (0.00, 0.00),
    "NORTH": (0.00, 0.23),
    "SOUTH": (0.00, -0.23),
    "EAST": (0.23, 0.00),
    "WEST": (-0.23, 0.00)
}

def is_known_position(row):
    for x, y in known_coordinates.values():
        if np.isclose(row["Predicted_X_m"], x) and \
           np.isclose(row["Predicted_Y_m"], y):
            return True
    return False

df["Is_Known_Calibration_Point"] = df.apply(
    is_known_position, axis=1
)

print("\n5. PREDICTION TYPE")
print(
    "Predictions matching one of five calibration points:",
    df["Is_Known_Calibration_Point"].sum()
)

print(
    "Predictions outside five calibration points:",
    (~df["Is_Known_Calibration_Point"]).sum()
)

print("\n" + "=" * 65)
print("INSPECTION COMPLETED")
print("=" * 65)
