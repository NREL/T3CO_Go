import io

import streamlit as st

# st.set_page_config(layout="wide")


def tco_breakdown_chart(i=0):
    # st.subheader("TCO Breakdown")
    (
        col1,
        col2,
    ) = st.columns([1, 1])

    with col2:
        x_group_col = st.selectbox(
            "Select horizontal group-by column",
            st.session_state.tc.group_columns,
            index=0,
            key=0 + 5 * i,
        )
    with col1:
        y_group_col = st.selectbox(
            "Select vertical group-by column",
            st.session_state.tc.group_columns,
            index=0,
            key=1 + 5 * i,
        )

    with st.expander("Advanced Settings"):
        col1, col2 = st.columns([1, 1])

        with col1:
            y_size = st.slider("Figure height", 1, 20, 6, 1)
        with col2:
            x_size = st.slider("Figure width", 1, 20, 3, 1)

        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            edgecolor_sel = st.selectbox(
                "Select edge color for the bars",
                st.session_state.tc.edgecolors,
                index=0,
                key=2 + 5 * i,
            )

        with col2:
            bar_width = st.slider(
                "Bar width as \% available space",
                0.0,
                1.0,
                step=0.05,
                key=3 + 5 * i,
                value=0.8,
            )
        with col3:
            legend_pos = st.slider(
                "Legend Horizontal Position",
                0.0,
                1.0,
                step=0.01,
                key=4 + 5 * i,
                value=0.25,
            )

    fig = st.session_state.tc.generate_tco_plots(
        x_group_col,
        y_group_col,
        edgecolor=edgecolor_sel,
        bar_width=bar_width,
        fig_x_size=x_size,
        fig_y_size=y_size,
        legend_pos=legend_pos,
    )

    st.pyplot(fig)

    img = io.BytesIO()
    fig.savefig(img, format="png", bbox_inches="tight", pad_inches=0.2)

    # try:
    st.download_button(
        key=10 + i,
        label="Download plot as PNG",
        data=img,
        file_name="plot.png",
        mime="image/png",
    )


def histogram_chart():
    hist_col = st.selectbox(
        "Select histogram column", st.session_state.tc.value_cols, key=5, index=21
    )
    bins = st.slider(
        "Adjust number of bins", key=6, min_value=1, max_value=50, value=20
    )
    show_pct = st.checkbox("Plot Percentage on Histogram")
    st.subheader("Histogram")

    fig = st.session_state.tc.generate_histogram(hist_col, bins, show_pct=show_pct)
    st.pyplot(fig)


def violin_chart():
    (
        col1,
        col2,
    ) = st.columns([1, 1])

    with col1:
        x_group_col = st.selectbox(
            "Select x-axis attribute",
            [col for col in st.session_state.tc.group_columns if col != "None"],
            index=0,
            key=0 + 20,
        )
    with col2:
        y_group_col = st.selectbox(
            "Select y-axis attribute", st.session_state.tc.value_cols, index=49, key=21
        )

    fig = st.session_state.tc.generate_violin_plot(
        x_group_col=x_group_col, y_group_col=y_group_col
    )
    st.pyplot(fig)


def visualization_dashboard():
    # plot_col = st.selectbox("Select column", tc.value_cols, key=7, index=14)
    st.header("Visualization")

    # st.subheader("T3CO Results")
    with st.expander("See T3CO Results Table"):
        st.write(st.session_state.tc.t3co_results)
        # vehicle_df = st.data_editor(st.session_state.results_df, key=3)

    st.markdown("#### T3COCharts")

    tab1, tab2, tab3 = st.tabs(["TCO Breakdown", "Histogram", "Violin Plots"])

    # TODO rename xaxis
    with tab1:
        tco_breakdown_chart()
    with tab2:
        histogram_chart()
    with tab3:
        violin_chart()


if "results_df" in st.session_state and st.session_state.results_df is not None:
    visualization_dashboard()
else:
    st.write("Upload T3CO Results file or run the tool")
