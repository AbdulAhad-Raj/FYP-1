
import pandas as pd
import numpy as np
import joblib

from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

print("=" * 65)
print("SENTINEL-X MODULE 3")
print("COMPLETE MODEL EVALUATION")
print("=" * 65)

folder = Path(__file__).parent
input_file = folder / "sentinel_x_validated_dataset.csv"

df = pd.read_csv(input_file)

required = ["Distance_m", "Tag_ID", "RSSI_dBm", "Session_ID"]

if not all(col in df.columns for col in required):
    raise ValueError("Required dataset columns are missing.")

if df[required].isnull().any().any():
    raise ValueError("Missing values detected.")

# --------------------------------------------------
# 1. VERIFY DATASET
# --------------------------------------------------

print("\n1. DATASET VERIFICATION")
print("-" * 45)

print("Total readings:", len(df))
print("\nSession counts:")
print(df["Session_ID"].value_counts().sort_index())

print("\nTag-distance-session counts:")
counts = df.groupby(
    ["Session_ID", "Tag_ID", "Distance_m"]
).size()

print(counts.to_string())

if len(df) != 1000:
    raise ValueError("Expected exactly 1000 readings.")

if set(df["Session_ID"].unique()) != {1, 2}:
    raise ValueError("Expected Session_ID values 1 and 2.")

if not (counts == 25).all() or len(counts) != 40:
    raise ValueError(
        "Expected 25 readings in each of 40 "
        "tag-distance-session combinations."
    )

# --------------------------------------------------
# 2. PREPARE FEATURES
# --------------------------------------------------

X = pd.get_dummies(
    df[["RSSI_dBm", "Tag_ID"]],
    columns=["Tag_ID"],
    dtype=int
)

feature_columns = list(X.columns)
y = df["Distance_m"]

# --------------------------------------------------
# 3. SHARED EVALUATION FUNCTION
# --------------------------------------------------

def evaluate_model(name, train_idx, test_idx, output_name):

    X_train = X.iloc[train_idx]
    X_test = X.iloc[test_idx]

    y_train = y.iloc[train_idx]
    y_test = y.iloc[test_idx]

    train_model = RandomForestRegressor(
        n_estimators=200,
        max_depth=8,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )

    train_model.fit(X_train, y_train)

    predictions = train_model.predict(X_test)

    errors = np.abs(
        y_test.to_numpy() - predictions
    )

    mae = mean_absolute_error(y_test, predictions)

    rmse = np.sqrt(
        mean_squared_error(y_test, predictions)
    )

    r2 = r2_score(y_test, predictions)

    within_05 = (errors <= 0.5).mean() * 100
    within_1 = (errors <= 1.0).mean() * 100

    results = pd.DataFrame({
        "Tag_ID": df.iloc[test_idx]["Tag_ID"].values,
        "Actual_Distance_m": y_test.to_numpy(),
        "Predicted_Distance_m": predictions,
        "Absolute_Error_m": errors,
        "Session_ID": df.iloc[test_idx]["Session_ID"].values
    })

    results.to_csv(
        folder / output_name,
        index=False
    )

    print("\n" + "=" * 65)
    print(name)
    print("=" * 65)

    print("Training readings:", len(train_idx))
    print("Testing readings:", len(test_idx))

    print(f"MAE: {mae:.3f} m")
    print(f"RMSE: {rmse:.3f} m")
    print(f"R2 Score: {r2:.3f}")

    print(f"Within 0.5 m: {within_05:.2f}%")
    print(f"Within 1.0 m: {within_1:.2f}%")

    print("\nPER-TAG PERFORMANCE")

    for tag in sorted(results["Tag_ID"].unique()):

        part = results[results["Tag_ID"] == tag]

        tag_mae = mean_absolute_error(
            part["Actual_Distance_m"],
            part["Predicted_Distance_m"]
        )

        tag_rmse = np.sqrt(
            mean_squared_error(
                part["Actual_Distance_m"],
                part["Predicted_Distance_m"]
            )
        )

        tag_within_1 = (
            part["Absolute_Error_m"] <= 1.0
        ).mean() * 100

        print(
            f"{tag}: "
            f"N={len(part)}, "
            f"MAE={tag_mae:.3f} m, "
            f"RMSE={tag_rmse:.3f} m, "
            f"Within 1m={tag_within_1:.2f}%"
        )

    print("\nPER-DISTANCE PERFORMANCE")

    for distance in sorted(results["Actual_Distance_m"].unique()):

        part = results[
            results["Actual_Distance_m"] == distance
        ]

        distance_mae = part["Absolute_Error_m"].mean()

        distance_within_1 = (
            part["Absolute_Error_m"] <= 1.0
        ).mean() * 100

        print(
            f"{distance} m: "
            f"N={len(part)}, "
            f"MAE={distance_mae:.3f} m, "
            f"Within 1m={distance_within_1:.2f}%"
        )

    print("\nPredictions saved:", output_name)

    return {
        "name": name,
        "model": train_model,
        "MAE": mae,
        "RMSE": rmse,
        "R2": r2,
        "Within_0.5m": within_05,
        "Within_1m": within_1,
        "train_count": len(train_idx),
        "test_count": len(test_idx)
    }


# --------------------------------------------------
# 4. EVALUATION A: STRATIFIED 75/25 SPLIT
# --------------------------------------------------

print("\n\nEVALUATION A: STRATIFIED 75/25 SPLIT")

strata = (
    df["Session_ID"].astype(str) + "_" +
    df["Tag_ID"].astype(str) + "_" +
    df["Distance_m"].astype(str)
)

all_indices = np.arange(len(df))

train_idx, test_idx = train_test_split(
    all_indices,
    test_size=0.25,
    random_state=42,
    stratify=strata
)

stratified_result = evaluate_model(
    "STRATIFIED 75/25 EVALUATION",
    train_idx,
    test_idx,
    "sentinel_x_stratified_predictions.csv"
)

# Save this candidate model separately.
joblib.dump(
    {
        "model": stratified_result["model"],
        "feature_columns": feature_columns,
        "target": "Distance_m",
        "evaluation": "Stratified 75/25"
    },
    folder / "sentinel_x_stratified_random_forest.pkl"
)

# --------------------------------------------------
# 5. EVALUATION B1: TRAIN SESSION 1, TEST SESSION 2
# --------------------------------------------------

session1_train = np.where(
    df["Session_ID"].to_numpy() == 1
)[0]

session2_test = np.where(
    df["Session_ID"].to_numpy() == 2
)[0]

session1_result = evaluate_model(
    "INDEPENDENT SESSION: TRAIN 1, TEST 2",
    session1_train,
    session2_test,
    "sentinel_x_session1_to_session2_predictions.csv"
)

# --------------------------------------------------
# 6. EVALUATION B2: TRAIN SESSION 2, TEST SESSION 1
# --------------------------------------------------

session2_train = np.where(
    df["Session_ID"].to_numpy() == 2
)[0]

session1_test = np.where(
    df["Session_ID"].to_numpy() == 1
)[0]

session2_result = evaluate_model(
    "INDEPENDENT SESSION: TRAIN 2, TEST 1",
    session2_train,
    session1_test,
    "sentinel_x_session2_to_session1_predictions.csv"
)

# --------------------------------------------------
# 7. FINAL COMPARISON
# --------------------------------------------------

comparison = pd.DataFrame([
    {
        "Evaluation": r["name"],
        "Training_Readings": r["train_count"],
        "Testing_Readings": r["test_count"],
        "MAE_m": r["MAE"],
        "RMSE_m": r["RMSE"],
        "R2": r["R2"],
        "Within_0.5m_Percent": r["Within_0.5m"],
        "Within_1m_Percent": r["Within_1m"]
    }
    for r in [
        stratified_result,
        session1_result,
        session2_result
    ]
])

comparison.to_csv(
    folder / "sentinel_x_evaluation_comparison.csv",
    index=False
)

print("\n\nFINAL EVALUATION COMPARISON")
print("=" * 65)
print(comparison.round(3).to_string(index=False))

print("\nALL EVALUATIONS COMPLETED.")
print("\nOriginal dataset and previous model files were not modified.")
print("=" * 65)
