# ============================================
# 🔋 Battery SOH Prediction — Final Model Script
# ============================================

import pandas as pd
import numpy as np
import time
import os
import pickle
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

# --------------------------------------------
# Create results folder
# --------------------------------------------
if not os.path.exists("results"):
    os.makedirs("results")

start = time.time()

# =====================================
# Data Preprocessing and Cleaning
# =====================================
data_path = os.path.join("data", "PulseBat Dataset.xlsx")
data = pd.read_excel(data_path)

print("Columns in dataset:", list(data.columns))

columns_to_use = [f"U{i}" for i in range(1, 22)] + ["SOH"]
data = data[columns_to_use]

print("\n✅ Selected columns:")
print(data.head())

# Handle missing values
before = data.shape[0]
data = data.dropna()
after = data.shape[0]
print(f"\nDropped {before - after} rows. Final shape: {data.shape}")

# Save cleaned data
cleaned_path = os.path.join("data", "Cleaned_PulseBat_Dataset.xlsx")
data.to_excel(cleaned_path, index=False)
print(f"Cleaned dataset saved as {cleaned_path}")

# =====================================
# Feature Preparation
# =====================================
X = data.loc[:, "U1":"U21"].to_numpy()
y = data["SOH"]

# Create data variants
unsorted_data = X.copy()
ascending_data = np.sort(X, axis=1)
descending_data = ascending_data[:, ::-1]

datasets = {
    "Unsorted": unsorted_data,
    "Ascending": ascending_data,
    "Descending": descending_data
}

# =====================================
# Train Models and Evaluate
# =====================================
best_model = None
best_r2 = -1
best_name = ""

for name, X_data in datasets.items():
    X_train, X_test, y_train, y_test = train_test_split(
        X_data, y, test_size=0.2, random_state=42
    )

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    r2 = r2_score(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)

    print(f"\n📊 {name} Data Evaluation:")
    print(f"R² Score: {r2:.4f}")
    print(f"MSE: {mse:.4f}")
    print(f"MAE: {mae:.4f}")

    if r2 > best_r2:
        best_model = model
        best_r2 = r2
        best_name = name
        best_y_test = y_test
        best_y_pred = y_pred

end = time.time()
print(f"\n✅ Best model: {best_name} (R² = {best_r2:.3f})")
print(f"⏱️ Execution time: {end - start:.2f}s")

# =====================================
# Save Model + Metrics
# =====================================
model_path = "battery_soh_model.pkl"
with open(model_path, "wb") as f:
    pickle.dump(best_model, f)

metrics = {
    "R²": round(best_r2, 4),
    "MAE": round(mean_absolute_error(best_y_test, best_y_pred), 4),
    "RMSE": round(np.sqrt(mean_squared_error(best_y_test, best_y_pred)), 4)
}

importance = {
    f"U{i+1}": abs(coef)
    for i, coef in enumerate(best_model.coef_)
}

with open("results/model_metrics.pkl", "wb") as f:
    pickle.dump({"metrics": metrics, "importance": importance}, f)

print(f"✅ Model saved as {model_path}")
print(f"✅ Metrics saved in results/model_metrics.pkl")

# =====================================
# Visualization Section
# =====================================
threshold = 0.6  # fixed for automation

# Classification
y_pred_class = np.where(best_y_pred >= threshold, "Healthy", "Unhealthy")
y_test_class = np.where(best_y_test >= threshold, "Healthy", "Unhealthy")

results_df = pd.DataFrame({
    "Actual SOH": best_y_test,
    "Predicted SOH": best_y_pred,
    "Actual Class": y_test_class,
    "Predicted Class": y_pred_class
})

# Scatter plot
plt.figure(figsize=(8, 6))
colors = np.where(best_y_pred >= threshold, 'green', 'red')
plt.scatter(best_y_test, best_y_pred, color=colors, edgecolor='black', alpha=0.7)
plt.plot([best_y_test.min(), best_y_test.max()], [best_y_test.min(), best_y_test.max()], 'r--', lw=2)
plt.axhline(y=threshold, color='orange', linestyle='--', lw=2)
plt.title("Actual vs Predicted SOH", fontsize=14)
plt.xlabel("Actual SOH")
plt.ylabel("Predicted SOH")
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig("results/Actual_vs_Predicted_SOH.png", dpi=300)
plt.close()

# Residuals
residuals = best_y_test - best_y_pred
plt.figure(figsize=(8, 5))
sns.histplot(residuals, bins=25, kde=True, color='skyblue', edgecolor='black', alpha=0.7)
plt.axvline(0, color='black', linestyle='--', lw=2)
plt.title("Residuals Distribution", fontsize=14)
plt.xlabel("Residual (Actual - Predicted)")
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig("results/Residuals_Distribution.png", dpi=300)
plt.close()

# Preview
print("\n🔋 Sample Predictions:\n", results_df.head(10))
print("\n✅ Training Complete. Ready for Deployment.")
