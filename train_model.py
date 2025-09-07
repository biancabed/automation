import pandas as pd
import pickle
from sklearn.ensemble import RandomForestRegressor

# Define sheet names and model filenames for each turbine
turbines = {
    "Nordex N100": {"sheet": "Nordex N100", "model": "model_nordex.pkl"},
    "Vestas V90": {"sheet": "Vestas V90", "model": "model_vestas.pkl"},
    "Repower M5": {"sheet": "Repower M5", "model": "model_repower.pkl"},
}

# Load all sheets from the Excel file
df_excel = pd.read_excel("formule_turbine.xlsx", sheet_name=None)

# Train a separate model for each turbine
for turbine, info in turbines.items():
    sheet = df_excel[info["sheet"]]
    x = sheet[["viteza"]]
    y = sheet["energie"]

    model = RandomForestRegressor()
    model.fit(x, y)

    # Save the trained model to a .pkl file
    with open(info["model"], "wb") as f:
        pickle.dump(model, f)

print("✅ All AI models have been successfully trained and saved.")
