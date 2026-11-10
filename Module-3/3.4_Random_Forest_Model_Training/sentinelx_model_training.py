
import pandas as pd
import numpy as np
import joblib

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from pathlib import Path

print("=" * 60)
print("SENTINEL-X MODULE 3")
print("RANDOM FOREST MODEL TRAINING")
print("=" * 60)

# --------------------------------------------------
# 1. LOAD VALIDATED DATASET
# --------------------------------------------------

folder = Path(__file__).parent

input_file = folder / "sentinel_x_validated_dataset.csv"

model_file = folder / "sentinel_x_random_forest.pkl"

prediction_file = folder / "sentinel_x_model_predictions.csv"

df = pd.read_csv(input_file)

required = [
    "Distance_m",
    "Tag_ID",
    "RSSI_dBm",
    "Session_ID"
]

if not all(col in df.columns for col in required):
    raise ValueError("Required dataset columns are missing.")

if df[required].isnull().any().any():
    raise ValueError("Dataset contains missing required values.")

print("\nDATASET INFORMATION")
print("-" * 40)
print("Total readings:", len(df))
print("Tags:", sorted(df["Tag_ID"].unique()))
print("Distances:", sorted(df["Distance_m"].unique()))
print("\nReadings per tag:")
print(df["Tag_ID"].value_counts().sort_index())

# --------------------------------------------------
# 2. PREPARE INPUT FEATURES AND TARGET
# --------------------------------------------------

X = df[["RSSI_dBm", "Tag_ID"]].copy()

y = df["Distance_m"].copy()

X = pd.get_dummies(
    X,
    columns=["Tag_ID"],
    dtype=int
)

# Keep a consistent feature order
feature_columns = list(X.columns)

# --------------------------------------------------
# 3. CREATE GROUP IDENTIFIERS
# --------------------------------------------------

# Keep readings from the same tag, distance,
# and collection session together.

groups = (
    df["Tag_ID"].astype(str) + "_" +
    df["Distance_m"].astype(str) + "_" +
    df["Session_ID"].astype(str)
)

# --------------------------------------------------
# 4. FIND A VALID 75/25 GROUP SPLIT
# --------------------------------------------------

print("\nSEARCHING FOR A VALID GROUP SPLIT...")

split_found = False

all_tags = set(df["Tag_ID"].unique())
all_distances = set(df["Distance_m"].unique())

for seed in range(42, 1042):

    splitter = GroupShuffleSplit(
        n_splits=1,
        test_size=0.25,
        random_state=seed
    )

    train_idx, test_idx = next(
        splitter.split(X, y, groups=groups)
    )

    train_tags = set(df.iloc[train_idx]["Tag_ID"])
    test_tags = set(df.iloc[test_idx]["Tag_ID"])

    train_distances = set(
        df.iloc[train_idx]["Distance_m"]
    )

    test_distances = set(
        df.iloc[test_idx]["Distance_m"]
    )

    # Require every tag and distance to appear
    # in both training and testing datasets.

    if (
        train_tags == all_tags
        and test_tags == all_tags
        and train_distances == all_distances
        and test_distances == all_distances
    ):
        split_found = True
        selected_seed = seed
        break

if not split_found:
    raise RuntimeError(
        "Could not find a valid group split. "
        "Check dataset group distribution."
    )

X_train = X.iloc[train_idx]
X_test = X.iloc[test_idx]

y_train = y.iloc[train_idx]
y_test = y.iloc[test_idx]

print("\nDATA SPLIT RESULTS")
print("-" * 40)
print("Selected random seed:", selected_seed)
print("Total readings:", len(df))
print("Training readings:", len(X_train))
print("Testing readings:", len(X_test))

print("\nTraining tag distribution:")
print(
    df.iloc[train_idx]["Tag_ID"]
    .value_counts()
    .sort_index()
)

print("\nTesting tag distribution:")
print(
    df.iloc[test_idx]["Tag_ID"]
    .value_counts()
    .sort_index()
)

print("\nTesting distance distribution:")
print(
    df.iloc[test_idx]["Distance_m"]
    .value_counts()
    .sort_index()
)

# --------------------------------------------------
# 5. CREATE RANDOM FOREST MODEL
# --------------------------------------------------

model = RandomForestRegressor(
    n_estimators=200,
    max_depth=8,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)

# --------------------------------------------------
# 6. TRAIN MODEL
# --------------------------------------------------

print("\nTRAINING RANDOM FOREST MODEL...")

model.fit(X_train, y_train)

print("Training completed successfully.")

# --------------------------------------------------
# 7. GENERATE TEST PREDICTIONS
# --------------------------------------------------

predictions = model.predict(X_test)

# --------------------------------------------------
# 8. CALCULATE OVERALL PERFORMANCE
# --------------------------------------------------

mae = mean_absolute_error(y_test, predictions)

rmse = np.sqrt(
    mean_squared_error(y_test, predictions)
)

r2 = r2_score(y_test, predictions)

errors = np.abs(
    y_test.to_numpy() - predictions
)

within_05 = np.mean(errors <= 0.5) * 100

within_1 = np.mean(errors <= 1.0) * 100

print("\nMODEL PERFORMANCE")
print("-" * 40)

print(f"MAE: {mae:.3f} metres")
print(f"RMSE: {rmse:.3f} metres")
print(f"R2 Score: {r2:.3f}")

print(f"Within 0.5 metre: {within_05:.2f}%")
print(f"Within 1 metre: {within_1:.2f}%")

# --------------------------------------------------
# 9. PERFORMANCE FOR EACH TAG
# --------------------------------------------------

print("\nPER-TAG PERFORMANCE")
print("-" * 40)

test_results = pd.DataFrame({
    "Tag_ID": df.iloc[test_idx]["Tag_ID"].values,
    "Actual_Distance_m": y_test.to_numpy(),
    "Predicted_Distance_m": predictions,
    "Absolute_Error_m": errors
})

for tag in sorted(test_results["Tag_ID"].unique()):

    tag_data = test_results[
        test_results["Tag_ID"] == tag
    ]

    tag_mae = mean_absolute_error(
        tag_data["Actual_Distance_m"],
        tag_data["Predicted_Distance_m"]
    )

    tag_rmse = np.sqrt(
        mean_squared_error(
            tag_data["Actual_Distance_m"],
            tag_data["Predicted_Distance_m"]
        )
    )

    tag_within_1 = (
        tag_data["Absolute_Error_m"] <= 1.0
    ).mean() * 100

    print(
        f"{tag}: "
        f"Readings={len(tag_data)}, "
        f"MAE={tag_mae:.3f} m, "
        f"RMSE={tag_rmse:.3f} m, "
        f"Within 1m={tag_within_1:.2f}%"
    )

# --------------------------------------------------
# 10. SAVE TRAINED MODEL
# --------------------------------------------------

joblib.dump(
    {
        "model": model,
        "feature_columns": feature_columns,
        "target": "Distance_m",
        "training_readings": len(X_train),
        "testing_readings": len(X_test),
        "split_seed": selected_seed
    },
    model_file
)

# --------------------------------------------------
# 11. SAVE ALL TEST PREDICTIONS
# --------------------------------------------------

test_results.to_csv(
    prediction_file,
    index=False
)

# --------------------------------------------------
# 12. FINAL VERIFICATION
# --------------------------------------------------

saved_predictions = pd.read_csv(prediction_file)

print("\nGENERATED FILES")
print("-" * 40)

print("Model file:")
print(model_file)

print("\nPrediction file:")
print(prediction_file)

print("\nPREDICTION FILE VERIFICATION")
print("-" * 40)

print("Saved prediction rows:", len(saved_predictions))

print("\nTags in prediction file:")
print(
    saved_predictions["Tag_ID"]
    .value_counts()
    .sort_index()
)

print("\nModule 3 model training completed.")
print("=" * 60)
