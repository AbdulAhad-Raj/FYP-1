
import pandas as pd
import numpy as np
import pickle

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

print("SENTINEL-X MODULE 3")
print("SESSION 1 RANDOM FOREST MODEL TRAINING")
print("=" * 50)

# 1. Load validated dataset
df = pd.read_csv("sentinel_x_validated_dataset.csv")

print("\nOriginal dataset readings:", len(df))

# 2. Keep Session 1 only
df = df[df["Session_ID"] == 1].copy()

print("Session 1 readings:", len(df))

# 3. Check dataset completeness
print("\nREADINGS PER TAG AND DISTANCE")
distribution = pd.crosstab(df["Tag_ID"], df["Distance_m"])
print(distribution)

# 4. Prepare input features and target
X = df[["RSSI_dBm", "Tag_ID"]].copy()

# One-hot encode tag IDs
X = pd.get_dummies(X, columns=["Tag_ID"], dtype=int)

# Ensure consistent feature columns
expected_columns = [
    "RSSI_dBm",
    "Tag_ID_TAG-01",
    "Tag_ID_TAG-02",
    "Tag_ID_TAG-03",
    "Tag_ID_TAG-04"
]

X = X.reindex(columns=expected_columns, fill_value=0)

y = df["Distance_m"]

# 5. Stratify by tag and actual distance
# This ensures every combination is represented in
# both training and testing datasets.
strata = (
    df["Tag_ID"].astype(str)
    + "_"
    + df["Distance_m"].astype(str)
)

# Check that every combination has enough readings
if strata.value_counts().min() < 2:
    raise ValueError("Some tag-distance combinations have too few readings.")

# 6. Split the dataset
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=strata
)

print("\nDATASET SPLIT")
print("Training readings:", len(X_train))
print("Testing readings:", len(X_test))

# 7. Train Random Forest
print("\nTraining Random Forest model...")

model = RandomForestRegressor(
    n_estimators=200,
    max_depth=8,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

# 8. Generate predictions
predictions = model.predict(X_test)

# 9. Evaluate model
mae = mean_absolute_error(y_test, predictions)
rmse = np.sqrt(mean_squared_error(y_test, predictions))
r2 = r2_score(y_test, predictions)

print("\nMODEL PERFORMANCE")
print("-" * 40)
print(f"MAE:  {mae:.3f} metres")
print(f"RMSE: {rmse:.3f} metres")
print(f"R2:   {r2:.3f}")

# 10. Save predictions
results = df.loc[X_test.index, ["Tag_ID"]].copy()

results["Actual_Distance_m"] = y_test
results["Predicted_Distance_m"] = predictions
results["Absolute_Error_m"] = np.abs(
    y_test.to_numpy() - predictions
)

results.to_csv(
    "sentinel_x_session1_predictions.csv",
    index=False
)

# 11. Save trained model separately
model_bundle = {
    "model": model,
    "feature_columns": expected_columns,
    "training_session": 1,
    "target": "Distance_m"
}

with open("sentinel_x_session1_random_forest.pkl", "wb") as file:
    pickle.dump(model_bundle, file)

# 12. Save evaluation summary
with open("sentinel_x_session1_metrics.txt", "w") as file:
    file.write("SENTINEL-X SESSION 1 MODEL EVALUATION\n")
    file.write(f"Total readings: {len(df)}\n")
    file.write(f"Training readings: {len(X_train)}\n")
    file.write(f"Testing readings: {len(X_test)}\n")
    file.write(f"MAE: {mae:.3f} metres\n")
    file.write(f"RMSE: {rmse:.3f} metres\n")
    file.write(f"R2: {r2:.3f}\n")

print("\nFILES GENERATED")
print("1. sentinel_x_session1_predictions.csv")
print("2. sentinel_x_session1_random_forest.pkl")
print("3. sentinel_x_session1_metrics.txt")

print("\nSESSION 1 MODEL TRAINING COMPLETED")
