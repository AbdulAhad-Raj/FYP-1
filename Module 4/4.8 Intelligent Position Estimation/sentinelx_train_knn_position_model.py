
import pandas as pd
import numpy as np
import joblib

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

# ==========================================================
# SENTINEL-X MODULE 4.8
# KNN TWO-DIMENSIONAL POSITION ESTIMATION
# ==========================================================

INPUT_FILE = "05_final_coordinate_labelled_calibration_dataset.csv"
MODEL_FILE = "sentinelx_knn_position_model.pkl"
PREDICTIONS_FILE = "06_knn_position_estimation_results.csv"

FEATURES = [
    "RSSI_SENSOR_01_dBm",
    "RSSI_SENSOR_02_dBm",
    "RSSI_SENSOR_03_dBm",
    "RSSI_SENSOR_04_dBm"
]

TARGETS = ["X_m", "Y_m"]

# ==========================================================
# 1. LOAD DATA
# ==========================================================

print("=" * 65)
print("SENTINEL-X KNN POSITION ESTIMATION")
print("=" * 65)

df = pd.read_csv(INPUT_FILE)
df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")

print("\nDataset loaded:", INPUT_FILE)
print("Total fingerprints:", len(df))

# ==========================================================
# 2. VALIDATE REQUIRED DATA
# ==========================================================

required_columns = FEATURES + TARGETS + [
    "Ground_Truth_Position",
    "Timestamp"
]

missing_columns = [
    col for col in required_columns if col not in df.columns
]

if missing_columns:
    raise ValueError(f"Missing columns: {missing_columns}")

if df[required_columns].isnull().any().any():
    raise ValueError("Missing values detected. Stop before training.")

if not np.isfinite(df[FEATURES + TARGETS].to_numpy()).all():
    raise ValueError("Non-finite numerical values detected.")

print("\nRequired columns: PASS")
print("Missing values: NONE")

# ==========================================================
# 3. CHRONOLOGICAL TRAIN / GAP / TEST SPLIT
# ==========================================================
# Within each position:
# First 65% = training
# Next 10%  = excluded temporal buffer
# Last 25%  = testing
#
# This avoids randomly mixing nearby observations.

train_parts = []
test_parts = []

print("\nCHRONOLOGICAL DATA SPLIT")

for position, group in df.groupby("Ground_Truth_Position"):

    group = group.sort_values("Timestamp").reset_index(drop=True)

    total = len(group)
    train_end = int(total * 0.65)
    test_start = int(np.ceil(total * 0.75))

    if train_end < 5 or test_start >= total:
        raise ValueError(
            f"Insufficient samples for position {position}"
        )

    train_group = group.iloc[:train_end].copy()
    test_group = group.iloc[test_start:].copy()

    train_parts.append(train_group)
    test_parts.append(test_group)

    print(
        f"{position:7s} | Total: {total:3d} | "
        f"Train: {len(train_group):3d} | "
        f"Buffer: {test_start - train_end:3d} | "
        f"Test: {len(test_group):3d}"
    )

train_df = pd.concat(train_parts, ignore_index=True)
test_df = pd.concat(test_parts, ignore_index=True)

X_train = train_df[FEATURES]
y_train = train_df[TARGETS]

X_test = test_df[FEATURES]
y_test = test_df[TARGETS]

print("\nTotal training fingerprints:", len(train_df))
print("Total testing fingerprints:", len(test_df))

# ==========================================================
# 4. BUILD KNN MODEL
# ==========================================================

model = Pipeline([
    ("scaler", StandardScaler()),
    ("knn", KNeighborsRegressor(
        n_neighbors=5,
        weights="distance",
        metric="euclidean"
    ))
])

# ==========================================================
# 5. TRAIN MODEL
# ==========================================================

print("\nTraining KNN model...")

model.fit(X_train, y_train)

print("Training completed successfully.")

# ==========================================================
# 6. PREDICT TEST POSITIONS
# ==========================================================

predictions = model.predict(X_test)

actual_xy = y_test.to_numpy()

error_x = predictions[:, 0] - actual_xy[:, 0]
error_y = predictions[:, 1] - actual_xy[:, 1]

radial_errors = np.sqrt(error_x**2 + error_y**2)

# ==========================================================
# 7. EVALUATE POSITION ACCURACY
# ==========================================================

mean_radial_error = np.mean(radial_errors)
median_radial_error = np.median(radial_errors)
rmse_radial = np.sqrt(np.mean(radial_errors**2))

mae_x = mean_absolute_error(
    actual_xy[:, 0], predictions[:, 0]
)

mae_y = mean_absolute_error(
    actual_xy[:, 1], predictions[:, 1]
)

within_10cm = np.mean(radial_errors <= 0.10) * 100
within_20cm = np.mean(radial_errors <= 0.20) * 100

# Constant-coordinate baseline:
# Predict the average training coordinate for every test row.

baseline_xy = np.tile(
    y_train.mean().to_numpy(),
    (len(y_test), 1)
)

baseline_errors = np.sqrt(
    np.sum((baseline_xy - actual_xy)**2, axis=1)
)

baseline_mean_error = np.mean(baseline_errors)

# ==========================================================
# 8. DISPLAY RESULTS
# ==========================================================

print("\n" + "=" * 65)
print("KNN POSITION ESTIMATION RESULTS")
print("=" * 65)

print(f"Test samples: {len(test_df)}")
print(f"Mean radial error: {mean_radial_error:.4f} m")
print(f"Median radial error: {median_radial_error:.4f} m")
print(f"Radial RMSE: {rmse_radial:.4f} m")
print(f"X coordinate MAE: {mae_x:.4f} m")
print(f"Y coordinate MAE: {mae_y:.4f} m")
print(f"Within 10 cm: {within_10cm:.2f}%")
print(f"Within 20 cm: {within_20cm:.2f}%")

print("\nBASELINE COMPARISON")
print(f"Mean-coordinate baseline error: {baseline_mean_error:.4f} m")
print(f"KNN mean radial error:          {mean_radial_error:.4f} m")

# ==========================================================
# 9. SAVE TEST PREDICTIONS
# ==========================================================

results = test_df[
    ["Timestamp", "Ground_Truth_Position", "X_m", "Y_m"]
].copy()

results = results.rename(columns={
    "X_m": "Actual_X_m",
    "Y_m": "Actual_Y_m"
})

results["Predicted_X_m"] = predictions[:, 0]
results["Predicted_Y_m"] = predictions[:, 1]

results["Error_X_m"] = error_x
results["Error_Y_m"] = error_y
results["Radial_Error_m"] = radial_errors

results.to_csv(PREDICTIONS_FILE, index=False)

# ==========================================================
# 10. SAVE TRAINED MODEL
# ==========================================================

model_bundle = {
    "model": model,
    "features": FEATURES,
    "targets": TARGETS,
    "algorithm": "KNeighborsRegressor",
    "n_neighbors": 5,
    "weights": "distance",
    "distance_metric": "euclidean",
    "coordinate_system": {
        "CENTRE": (0.0, 0.0),
        "NORTH": (0.0, 0.23),
        "SOUTH": (0.0, -0.23),
        "EAST": (0.23, 0.0),
        "WEST": (-0.23, 0.0)
    }
}

joblib.dump(model_bundle, MODEL_FILE)

# ==========================================================
# 11. COMPLETION
# ==========================================================

print("\nOUTPUT FILES")
print("Model:", MODEL_FILE)
print("Predictions:", PREDICTIONS_FILE)

print("\n" + "=" * 65)
print("KNN POSITION ESTIMATION COMPLETED")
print("Source calibration dataset was not modified.")
print("This is an initial chronological holdout evaluation.")
print("The model has not yet been independently validated.")
print("=" * 65)
