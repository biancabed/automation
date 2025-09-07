import zipfile
import os

# Unzip models if not already extracted
def unzip_model(zip_name, pkl_name):
    if not os.path.exists(pkl_name):
        with zipfile.ZipFile(zip_name, 'r') as zip_ref:
            zip_ref.extractall()

unzip_model("model_nordex.zip", "model_nordex.pkl")
unzip_model("model_vestas.zip", "model_vestas.pkl")
unzip_model("model_repower.zip", "model_repower.pkl")


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from calcul_parc_eolian import calculate_energy

# Turbine data: rotor area (m²), number of turbines, and Excel column for wind speeds
turbine_data = {
    "Nordex N100 (2.5 MW)": {"A": 7854, "N": 12, "col": "v75"},
    "Vestas V90 (3 MW)": {"A": 6362, "N": 10, "col": "v90"},
    "Repower M5 (5 MW)": {"A": 12469, "N": 6, "col": "v100"},
}

st.title("💨 Comparative Energy Output Analysis – 30 MW Wind Farm")

st.markdown(""" 🎯 Purpose of this application:
This tool compares the annual energy output of three wind farm configurations, each totaling 30 MW, using only one turbine type:

- 12 × Nordex N100 (2.5 MW)  
- 10 × Vestas V90 (3 MW)  
- 6 × Repower M5 (5 MW)  

Each turbine uses wind speed data measured at its own hub height:
- 75 m for Nordex N100  
- 90 m for Vestas V90  
- 100 m for Repower M5
""")



# Load wind speed data from Excel
try:
    df = pd.read_excel("viteze.xlsx", sheet_name="Date")

    results = {}

    for turbine_name, data in turbine_data.items():
        col = data["col"]
        A = data["A"]
        N = data["N"]
        

        if col not in df.columns:
            st.error(f" The file must contain a column named '{col}' for {turbine_name}.")
            continue

        wind_speeds = df[col].values
        total_energy = calculate_energy(wind_speeds, A, N)
        results[turbine_name] = total_energy

    # Create a nice table
    results_df = pd.DataFrame.from_dict(results, orient='index', columns=["Energy Output (MWh/year)"])
    results_df.index.name = "Turbine Type"
    results_df = results_df.round(2)

    st.write("📊 Estimated Annual Energy Output (MWh/year):")
    st.dataframe(results_df.style.format("{:,.2f}"))

    # Plot bar chart
    fig, ax = plt.subplots()
    ax.bar(results_df.index, results_df["Energy Output (MWh/year)"])
    ax.set_ylabel("Energy Output (MWh/year)")
    ax.set_xlabel("Turbine Type")
    ax.set_title("Comparative Analysis of Turbine Types")
    st.pyplot(fig)

except Exception as e:
    st.error(f" An unexpected error occurred: {e}")

import streamlit as st
import pandas as pd
import pickle

st.header("🤖 Estimated Annual Energy Output Using AI (MWh/year)")

uploaded_file = st.file_uploader("Upload wind speed Excel file", type=["xlsx"])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file, sheet_name="Date")

        # Check required columns
        required_cols = ["v75", "v90", "v100"]
        if not all(col in df.columns for col in required_cols):
            st.error(" The uploaded file must contain the columns: 'v75', 'v90', 'v100'.")
        else:
            # Load AI models
            with open("model_nordex.pkl", "rb") as f1:
                model_nordex = pickle.load(f1)
            with open("model_vestas.pkl", "rb") as f2:
                model_vestas = pickle.load(f2)
            with open("model_repower.pkl", "rb") as f3:
                model_repower = pickle.load(f3)

            # Prepare data
            df_nordex = df[["v75"]].rename(columns={"v75": "viteza"})
            df_vestas = df[["v90"]].rename(columns={"v90": "viteza"})
            df_repower = df[["v100"]].rename(columns={"v100": "viteza"})

            # Predict energy (Wh)
            pred_nordex = model_nordex.predict(df_nordex).sum()
            pred_vestas = model_vestas.predict(df_vestas).sum()
            pred_repower = model_repower.predict(df_repower).sum()

            # Convert to MWh
            pred_nordex /= 1_000_000
            pred_vestas /= 1_000_000
            pred_repower /= 1_000_000

            # Show results
            results = pd.DataFrame({
                "Turbine": ["Nordex N100", "Vestas V90", "Repower M5"],
                "Predicted Output (MWh/year)": [
                    round(pred_nordex, 2),
                    round(pred_vestas, 2),
                    round(pred_repower, 2)
                ]
            })

            st.table(results)

    except Exception as e:
        st.error(f" Error: {e}")

# Only run this part if AI predictions are ready
if 'pred_nordex' in locals() and 'pred_vestas' in locals() and 'pred_repower' in locals():
    classic_results = {
        "Nordex N100": 75208.31,
        "Vestas V90": 58402.40,
        "Repower M5": 77244.98
    }

    ai_results = {
        "Nordex N100": pred_nordex,
        "Vestas V90": pred_vestas,
        "Repower M5": pred_repower,
    }

    comparison_data = []
    for turbine in classic_results:
        classic = classic_results[turbine]
        ai = ai_results[turbine]
        diff_abs = ai - classic
        diff_pct = (diff_abs / classic) * 100
        comparison_data.append({
            "Turbine": turbine,
            "Classic (MWh/year)": round(classic, 2),
            "AI (MWh/year)": round(ai, 2),
            "Absolute Difference": round(diff_abs, 2),
            "Relative Difference (%)": round(diff_pct, 2)
        })

    comparison_df = pd.DataFrame(comparison_data)
    st.markdown(" Comparative Report: Classic vs AI Estimated Output")
    st.dataframe(comparison_df)
else:
    st.warning(" Please upload the wind speed file to enable AI prediction comparison.")
