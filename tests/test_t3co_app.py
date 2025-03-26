import subprocess
import re
import time
import requests
import pytest


@pytest.fixture(scope="module")
def streamlit_app():
    """
    Fixture that starts the t3co_go Streamlit app using the custom command,
    waits until it is serving, and then yields the base URL.
    After tests complete, the process is terminated.
    """
    # Start the app with the custom command
    process = subprocess.Popen(
        ["run_t3co_go"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    port = None
    start_time = time.time()

    # Wait up to 30 seconds for the app to start and print its URL
    while time.time() - start_time < 30:
        line = process.stdout.readline()
        if not line:
            time.sleep(0.1)
            continue
        # Example expected output: "Local URL: http://localhost:8501"
        match = re.search(r"Local URL:\s+http://localhost:(\d+)", line)
        if match:
            port = int(match.group(1))
            break

    if port is None:
        process.terminate()
        pytest.fail("Streamlit app did not start within timeout.")

    base_url = f"http://localhost:{port}"
    yield base_url

    # Cleanup: terminate the streamlit process
    process.terminate()
    process.wait(timeout=5)


def test_app_responds(streamlit_app):
    """
    Test that the app responds to a GET request on its base URL.
    """
    response = requests.get(streamlit_app)
    # Check that the HTTP status code is OK (200)
    assert response.status_code == 200
    # Optionally, verify that some expected text appears on the page.
    # This could be text that you know your app renders.
    expected_texts = ["Streamlit", "T3Co", "t3co_go"]
    assert any(text in response.text for text in expected_texts)
