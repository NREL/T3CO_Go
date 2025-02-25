import runpy
runpy.run_module('streamlit.cli')
import streamlit.cli_util
import click
click.pass_context
if __name__ == '__main__':
    streamlit.cli_util._main_run_clExplicit('t3co_charts_app.py', 'streamlit run')