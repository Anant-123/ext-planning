import streamlit as st
import numpy as np
import plotly.graph_objs as go
import pandas as pd
import os
from datetime import datetime

# Page configuration
st.set_page_config(page_title="Billet Recovery Calculator", layout="wide", page_icon="🧮")

# Custom CSS styling
st.markdown("""
    <style>
        .main {background-color: #f9f9f9;}
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .stDataFrame {background-color: white; border-radius: 10px; padding: 10px;}
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown("<h1 style='text-align: center; color: #003366;'> Maximising Billet Recovery</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #666666;'>Downstream Extrusion </h4>", unsafe_allow_html=True)
st.markdown("---")

# Fixed values
conversion_factor = 1.1115
billet_lengths = [80, 78, 76, 75, 73, 70, 67, 65, 63, 60, 58, 55, 53, 50, 48]

# Sidebar user inputs
st.sidebar.header("🔧 Input Parameters")
cut_length = st.sidebar.number_input("Cut Length (m)", min_value=0.001, step=0.01, format="%.3f")
num_holes = st.sidebar.number_input("Number of Holes in Die", min_value=1, step=1)
kg_per_m = st.sidebar.number_input("kg/m", min_value=0.001, step=0.01, format="%.3f")
caustic_etching = st.sidebar.radio("Is Caustic Etching applied?", ['Yes', 'No'])
butt_weight = st.sidebar.number_input("The Butt weight (Kg)", min_value=1, value=4, step=1)
optimize=st.sidebar.button("🚀 Find Optimized Billet")

# Rounding logic
rounding_option = 2 if caustic_etching == 'Yes' else 1

# Core logic
if optimize and cut_length > 0 and num_holes > 0 and kg_per_m > 0:
    best_billet_length = None
    max_recovery = 0
    recovery_results = {}
    margin_results = {}
    pcs_results = {}

    for b in billet_lengths:
        billet_wt = b * conversion_factor
        output_len = (billet_wt - butt_weight) / (num_holes * kg_per_m)
        output_pcs = output_len / cut_length

        if 1 < output_pcs < 2:
            output_pcs_margin = np.floor(output_pcs)
        elif rounding_option == 1:
            output_pcs_margin = np.floor(output_pcs)
        else:
            output_pcs_margin = np.floor(output_pcs) - 1

        output_pcs_margin = max(0, output_pcs_margin)
        margin_length = output_len - (output_pcs_margin * cut_length)
        output_wt = output_pcs_margin * cut_length * num_holes * kg_per_m
        recovery = (output_wt / billet_wt) * 100

        recovery_results[b] = recovery
        margin_results[b] = margin_length
        pcs_results[b] = int(output_pcs_margin)

        if recovery > max_recovery and margin_length > 0.15*output_len:
            max_recovery = recovery
            best_billet_length = b

    # Display optimal results using st.metric
    st.subheader("📈 Optimal Result")
    if best_billet_length is not None:
    
        col1, col2, col3 = st.columns(3)
        col1.metric("Optimal Billet Length (cm)", f"{best_billet_length}")
        col2.metric("Max Recovery (%)", f"{max_recovery:.2f}")
        col3.metric("Pieces per Billet", f"{pcs_results[best_billet_length]}")

    #     # Log the results
    #     log_entry = {
    #         "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    #         "Cut Length (m)": cut_length,
    #         "Number of Holes": num_holes,
    #         "kg/m": kg_per_m,
    #         "Caustic Etching": caustic_etching,
    #         "Butt Weight (Kg)": butt_weight,
    #         "Optimal Billet Length (m)": best_billet_length,
    #         "Max Recovery (%)": round(max_recovery, 2),
    #         "Margin Length (m)": round(margin_results[best_billet_length], 2),
    #         "Pieces per Billet": pcs_results[best_billet_length]
    #     }

    #     log_df = pd.DataFrame([log_entry])

    #     log_file = "billet_optimisation_log.csv"
    #     if os.path.exists(log_file):
    #         log_df.to_csv(log_file, mode='a', header=False, index=False)
    #     else:
    #         log_df.to_csv(log_file, index=False)

    #     st.success("✅ Results logged successfully!")
    # else:
    #     st.warning("⚠️ No billet length meets the criteria of margin length > 1 meter.")


    # Summary Table
    st.subheader("🧾 Summary Table")
    df_summary = pd.DataFrame({
        "Billet Length (cm)": billet_lengths,
        "Margin Length (m)": [round(margin_results[b], 2) for b in billet_lengths],
        "Recovery (%)": [round(recovery_results[b], 2) for b in billet_lengths],
        "Pieces": [pcs_results[b] for b in billet_lengths]
    }).sort_values(by="Recovery (%)", ascending=False)

    def highlight_optimal(row):
        return ['background-color: #ffe599' if row['Billet Length (cm)'] == best_billet_length else '' for _ in row]

    st.dataframe(df_summary.style.apply(highlight_optimal, axis=1), height=400)

    # Plotly Chart
    st.subheader("📊 Visual Comparison")

    

    # Bar trace with data labels
    trace1 = go.Bar(
        x=df_summary["Billet Length (cm)"],
        y=df_summary["Recovery (%)"],
        name="Recovery (%)",
        marker=dict(color='rgba(0, 200, 83, 0.7)', line=dict(width=1, color='black')),
        text=df_summary["Recovery (%)"].round(2),
        textposition='auto',
        yaxis='y1'
    )

    # Layout customization
    layout = go.Layout(
        title="Billet Length vs Recovery",
        xaxis=dict(
            title="Billet Length (cm)",
            showgrid=False,          
            tickvals=df_summary["Billet Length (cm)"],
            ticktext=df_summary["Billet Length (cm)"],
            tickangle=0,             
            linecolor='black',
            linewidth=1
        ),
        yaxis=dict(
            title="Recovery (%)",
            showgrid=False,          
            showline=True,
            linecolor='black',
            linewidth=1
        ),
        plot_bgcolor='white',        
        paper_bgcolor='white',
        legend=dict(
            x=0.5,
            y=1.1,
            orientation='h',
            xanchor='center'
        ),
        margin=dict(t=40, b=80, l=60, r=60),
    )

    fig = go.Figure(data=[trace1], layout=layout)
    st.plotly_chart(fig, use_container_width=True)
    
else:
    st.warning("Please enter valid values for all inputs to calculate recovery.")
