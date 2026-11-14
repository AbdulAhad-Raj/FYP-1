
import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

print("SENTINEL-X")
print("SESSION-BASED MODEL VALIDATION")
print("=" * 55)

# 1. Load the original complete dataset
df = pd.read_csv("sentinel_x_validated_dataset.csv")

# 2. Check required columns
required = [
    "Session_ID",
    "Tag_ID",
    "Distance_m",
    "RSSI_dBm"
]

for col in required:
    if col not in df.columns:
        raise ValueError(f"Missing column: {col}")

# 3. Display session distribution
print("\nSESSION DISTRIBUTION")
print(df["Session_ID"].value_counts().sort_index())

# 4. Confirm each session contains all tag-distance combinations
coverage = df.groupby(
    ["Session_ID", "Tag_ID", "Distance_m"]
).size().unstack("Distance_m", fill_value=0)

print("\nSESSION TAG-DISTANCE COVERAGE")
print(coverage)

# 5. Split by collection session
train = df[df["Session_ID"] == 1].copy()
test = df[df["Session_ID"] == 2].copy()

if train.empty or test.empty:
    raise ValueError("Session 1 or Session 2 is missing.")

if set(train["Tag_ID"]) != set(test["Tag_ID"]):
    raise ValueError("Training and testing tags do not match.")

if set(train["Distance_m"]) != set(test["Distance_m"]):
    raise ValueError("Training and testing distances do not match.")

# 6. One-hot encode tag IDs
X_train = pd.get_dummies(
    train[["RSSI_dBm", "Tag_ID"]],
    columns=["Tag_ID"]
)

X_test = pd.get_dummies(
    test[["RSSI_dBm", "Tag_ID"]],
    columns=["Tag_ID"]
)

X_test = X_test.reindex(
    columns=X_train.columns,
    fill_value=0
)

y_train = train["Distance_m"]
y_test = test["Distance_m"]

print("\nDATA SPLIT")
print("Training readings:", len(train))
print("Testing readings:", len(test))

# 7. Train a fresh Random Forest model
model = RandomForestRegressor(
    n_estimators=200,
    max_depth=8,
    min_samples_leaf=2,
    random_state=42
)

model.fit(X_train, y_train)

# 8. Predict distances
predictions = model.predict(X_test)

# 9. Calculate overall performance
mae = mean_absolute_error(y_test, predictions)
rmse = np.sqrt(mean_squared_error(y_test, predictions))
r2 = r2_score(y_test, predictions)

errors = np.abs(y_test.to_numpy() - predictions)

print("\nOVERALL SESSION-BASED RESULTS")
print("MAE:", round(mae, 3), "m")
print("RMSE:", round(rmse, 3), "m")
print("R2:", round(r2, 3))
print("Within 0.5m:", round(np.mean(errors <= 0.5) * 100, 2), "%")
print("Within 1m:", round(np.mean(errors <= 1.0) * 100, 2), "%")

# 10. Distance-wise results
results = []

for distance in sorted(y_test.unique()):

    mask = y_test.to_numpy() == distance

    actual = y_test.to_numpy()[mask]
    predicted = predictions[mask]
    error = np.abs(actual - predicted)

    results.append({
        "Actual_Distance_m": distance,
        "Readings": len(actual),
        "MAE_m": round(mean_absolute_error(actual, predicted), 3),
        "RMSE_m": round(
            np.sqrt(mean_squared_error(actual, predicted)), 3
        ),
        "Within_0.5m_%": round(np.mean(error <= 0.5) * 100, 2),
        "Within_1m_%": round(np.mean(error <= 1.0) * 100, 2)
    })

distance_results = pd.DataFrame(results)

print("\nDISTANCE-WISE RESULTS")
print(distance_results.to_string(index=False))

# 11. Tag-wise results
prediction_df = pd.DataFrame({
    "Tag_ID": test["Tag_ID"].to_numpy(),
    "Actual_Distance_m": y_test.to_numpy(),
    "Predicted_Distance_m": predictions,
    "Absolute_Error_m": errors
})

tag_results = prediction_df.groupby("Tag_ID").agg(
    Readings=("Absolute_Error_m", "count"),
    MAE_m=("Absolute_Error_m", "mean")
).reset_index()

tag_results["MAE_m"] = tag_results["MAE_m"].round(3)

print("\nTAG-WISE RESULTS")
print(tag_results.to_string(index=False))

# 12. Save independent validation outputs
prediction_df.to_csv(
    "sentinelx_session2_predictions.csv",
    index=False
)

distance_results.to_csv(
    "sentinelx_session2_distance_results.csv",
    index=False
)

tag_results.to_csv(
    "sentinelx_session2_tag_results.csv",
    index=False
)

print("\nVALIDATION COMPLETED")
print("Generated three independent evaluation files.")
