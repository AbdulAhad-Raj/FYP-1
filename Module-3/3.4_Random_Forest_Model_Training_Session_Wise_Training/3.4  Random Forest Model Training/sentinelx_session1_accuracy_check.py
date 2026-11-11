
import pandas as pd
import numpy as np

df = pd.read_csv("sentinel_x_session1_predictions.csv")

errors = df["Absolute_Error_m"]

print("SENTINEL-X DISTANCE ACCURACY CHECK")
print("=" * 45)

total = len(df)

within_half = (errors <= 0.5).sum()
within_one = (errors <= 1.0).sum()

print(f"\nTotal test predictions: {total}")

print(
    f"Within 0.5 metres: {within_half} "
    f"({within_half / total * 100:.2f}%)"
)

print(
    f"Within 1 metre: {within_one} "
    f"({within_one / total * 100:.2f}%)"
)

print("\nACCURACY BY DISTANCE")

df["Within_0.5m"] = errors <= 0.5
df["Within_1m"] = errors <= 1.0

summary = df.groupby("Actual_Distance_m").agg(
    Total=("Absolute_Error_m", "count"),
    Within_0_5m=("Within_0.5m", "sum"),
    Within_1m=("Within_1m", "sum")
)

summary["Within_0_5m_Percent"] = (
    summary["Within_0_5m"] / summary["Total"] * 100
)

summary["Within_1m_Percent"] = (
    summary["Within_1m"] / summary["Total"] * 100
)

print(summary.round(2))

print("\nACCURACY CHECK COMPLETED")
