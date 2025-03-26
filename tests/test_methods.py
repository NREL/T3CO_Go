#   ---------------------------------------------------------------------------------
#   Copyright (c) Microsoft Corporation. All rights reserved.
import subprocess
import time
import requests


def test_streamlit_app():
    """
    Test to ensure the t3co_go Streamlit app can be opened and is running.
    This test starts the Streamlit app in a subprocess, waits for it to initialize,
    and checks if the app is accessible via HTTP.
    """
    # Start the Streamlit app in a subprocess
    process = subprocess.Popen(
        ["run_t3co_go"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        # Wait for the app to initialize
        time.sleep(5)

        # Check if the app is accessible
        response = requests.get("http://localhost:8501")
        assert response.status_code == 200, "Streamlit app is not accessible"

    finally:
        # Terminate the Streamlit app process
        process.terminate()
        process.wait()
