
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

print("SENTINEL-X MODULE 3")
print("RANDOM FOREST MODEL TRAINING")
print("-" * 45)

# 1. Load validated dataset
df = pd.read_csv("sentinel_x_validated_dataset.csv")

# 2. Verify required columns
required = [
    "Distance_m",
    "Tag_ID",
    "RSSI_dBm",
    "Session_ID"
]

if not all(col in df.columns for col in required):
    raise ValueError("Required dataset columns are missing.")

# 3. Prepare input and target
X = df[["RSSI_dBm", "Tag_ID"]].copy()
y = df["Distance_m"]

# 4. Encode tag identity
X = pd.get_dummies(
    X,
    columns=["Tag_ID"],
    dtype=int
)

# 5. Group readings by tag, distance and session.
# This keeps each measurement group together
# instead of splitting similar readings randomly.
groups = (
    df["Tag_ID"].astype(str) + "_" +
    df["Distance_m"].astype(str) + "_" +
    df["Session_ID"].astype(str)
)

# 6. Split training and testing data
splitter = GroupShuffleSplit(
    n_splits=1,
    test_size=0.25,
    random_state=42
)

train_idx, test_idx = next(
    splitter.split(X, y, groups=groups)
)

X_train = X.iloc[train_idx]
X_test = X.iloc[test_idx]

y_train = y.iloc[train_idx]
y_test = y.iloc[test_idx]

print("\nDataset information")
print("Total readings:", len(df))
print("Training readings:", len(X_train))
print("Testing readings:", len(X_test))

# 7. Create Random Forest model
model = RandomForestRegressor(
    n_estimators=200,
    max_depth=8,
    min_samples_leaf=2,
    random_state=42
)

# 8. Train model
print("\nTraining model...")
model.fit(X_train, y_train)

# 9. Predict test data
predictions = model.predict(X_test)

# 10. Evaluate model
mae = mean_absolute_error(y_test, predictions)
rmse = np.sqrt(mean_squared_error(y_test, predictions))
r2 = r2_score(y_test, predictions)

print("\nMODEL PERFORMANCE")
print("-" * 30)
print(f"MAE: {mae:.3f} metres")
print(f"RMSE: {rmse:.3f} metres")
print(f"R2 Score: {r2:.3f}")

# 11. Save trained model and feature order
joblib.dump(
    {
        "model": model,
        "feature_columns": list(X.columns)
    },
    "sentinel_x_random_forest.pkl"
)

# 12. Save test predictions
results = pd.DataFrame({
    "Tag_ID": df.iloc[test_idx]["Tag_ID"].values,
    "Actual_Distance_m": y_test.values,
    "Predicted_Distance_m": predictions,
    "Absolute_Error_m": np.abs(
        y_test.values - predictions
    )
})

results.to_csv(
    "sentinel_x_model_predictions.csv",
    index=False
)

print("\nFiles generated:")
print("sentinel_x_random_forest.pkl")
print("sentinel_x_model_predictions.csv")

print("\nModel training completed.")
