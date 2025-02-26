import argparse
import time
from pathlib import Path

import pandas as pd
import streamlit as st
from t3co.visualization.charts import T3COCharts

from t3co_go.run.run_t3co import run_t3co

# st.set_page_config(layout="wide")

start = time.time()
parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    prog="T3CO Go",
    description="""The home.py module is the Visualization script for T3CO""",
)
parser.add_argument(
    "--input-file",
    type=str,
    default=None,
    help="Filepath of T3CO results CSV file",
)
args = parser.parse_args()
if args.input_file:
    df = pd.read_csv(args.input_file)
else:
    df = None

st.title("T3CO-Go")

purpose = st.radio(
    "How do you want to use the T3CO-Go Dashboard?",
    ["Run T3CO tool", "Visualize Existing Results"],
    captions=[
        "Allows users to modify input files and run T3CO",
        "Helps visualize T3CO results based on a results CSV file",
    ],
)

if purpose == "Visualize Existing Results":
    uploaded_file = st.file_uploader("Choose a T3CO results file")
    if uploaded_file is not None or df is not None:
        st.subheader(f"Filename: {uploaded_file.name} ")
        st.session_state.results_df = pd.read_csv(uploaded_file)
        st.session_state.tc = T3COCharts(results_df=st.session_state.results_df)

        print(f"uploaded_file: {uploaded_file.name}")
        st.switch_page("pages/visualize_results.py")


else:
    st.header("Run T3CO")
    vehicle_file = (
        Path(__file__).parents[3]
        / "demo_inputs/inputs/demo/Demo_FY22_vehicle_model_assumptions.csv"
    )
    scenario_file = (
        Path(__file__).parents[3]
        / "demo_inputs/inputs/demo/Demo_FY22_scenario_assumptions.csv"
    )
    config_file = Path(__file__).parents[3] / "demo_inputs/T3COConfig.csv"

    st.session_state.vehicle_df = pd.read_csv(vehicle_file)
    st.session_state.scenario_df = pd.read_csv(scenario_file)
    st.session_state.config_df = pd.read_csv(config_file)
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("Vehicle Inputs")

    with col2:
        st.text("")
        if st.button("Upload Vehicle File", key=0):
            uploaded_file = st.file_uploader("Choose a Vehicle Input file")
            if uploaded_file is not None:
                st.subheader(f"Vehicle File: {uploaded_file.name} ")
                st.session_state.vehicle_df = pd.read_csv(uploaded_file)

                print(f"uploaded_file: {uploaded_file.name}")

    with st.expander("See Vehicle Assumptions"):
        vehicle_df = st.data_editor(st.session_state.vehicle_df, key=3)

    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader("Scenario Inputs")
    with col2:
        st.text("")
        if st.button("Upload Scenario File", key=1):
            uploaded_file = st.file_uploader("Choose a Scenario Input file")
            if uploaded_file is not None:
                st.subheader(f"Scenario File: {uploaded_file.name} ")
                st.session_state.scenario_df = pd.read_csv(uploaded_file)

                print(f"uploaded_file: {uploaded_file.name}")

    with st.expander("See Scenario Assumptions"):
        scenario_df = st.data_editor(st.session_state.scenario_df, key=4)

    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("Config Inputs")
    with col2:
        st.text("")
        if st.button("Upload Config File", key=2):
            uploaded_file = st.file_uploader("Choose a Scenario Input file")
            if uploaded_file is not None:
                st.subheader(f"Config File: {uploaded_file.name} ")
                st.session_state.config_df = pd.read_csv(uploaded_file)

                print(f"uploaded_file: {uploaded_file.name}")

    edited_config_df = st.data_editor(
        st.session_state.config_df,
        key=5,
        column_config={
            "command": "Streamlit Command",
            "selections": st.column_config.TextColumn(),
        },
        # num_rows='dynamic'
    )

    col1, col2 = st.columns([2, 2])

    with col1:
        analysis_id = st.selectbox(
            "Select the analysis_id from T3COConfig",
            (st.session_state.config_df["analysis_id"].astype(int)),
        )

        run_multi = st.checkbox(
            "Run multiprocessing",
        )

    edited_config_df.to_csv(config_file, index=False)
    # Every form must have a submit button.

    if st.button("Run T3CO"):
        results_df = run_t3co(
            analysis_id, config_file, save_results=True, run_multi=run_multi
        )

        st.session_state.results_df = results_df
        # print(f"scenario_gvwr_kg: {results_df['scenario_gvwr_kg'].dtype}")
        # st.dataframe(results_df)
        st.session_state.tc = T3COCharts(results_df=st.session_state.results_df)
        st.switch_page("pages/visualize_results.py")
