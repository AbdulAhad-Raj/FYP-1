
import pandas as pd
import numpy as np

df = pd.read_csv("sentinel_x_session1_predictions.csv")

df["Error_m"] = (
    df["Predicted_Distance_m"] - df["Actual_Distance_m"]
)

print("SENTINEL-X SESSION 1 DETAILED EVALUATION")
print("=" * 55)

print("\n1. PERFORMANCE BY ACTUAL DISTANCE")
print(
    df.groupby("Actual_Distance_m").agg(
        Readings=("Error_m", "count"),
        MAE=("Absolute_Error_m", "mean"),
        RMSE=("Error_m", lambda x: np.sqrt(np.mean(x**2))),
        Mean_Error=("Error_m", "mean")
    ).round(3)
)

print("\n2. PERFORMANCE BY TAG")
print(
    df.groupby("Tag_ID").agg(
        Readings=("Error_m", "count"),
        MAE=("Absolute_Error_m", "mean"),
        RMSE=("Error_m", lambda x: np.sqrt(np.mean(x**2)))
    ).round(3)
)

print("\n3. PERFORMANCE BY TAG AND DISTANCE")
print(
    df.groupby(["Tag_ID", "Actual_Distance_m"]).agg(
        Readings=("Error_m", "count"),
        MAE=("Absolute_Error_m", "mean")
    ).round(3)
)

print("\n4. PREDICTION RANGE")
print("Minimum predicted distance:",
      round(df["Predicted_Distance_m"].min(), 3), "m")

print("Maximum predicted distance:",
      round(df["Predicted_Distance_m"].max(), 3), "m")

print("\n5. SAMPLE PREDICTIONS")
print(df.head(15).round(3).to_string(index=False))

print("\nDETAILED EVALUATION COMPLETED")
