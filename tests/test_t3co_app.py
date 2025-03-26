import subprocess
import re
import time
import requests
import pytest
import os


@pytest.fixture(scope="module")
def streamlit_app():
    """
    Fixture that starts the t3co_go Streamlit app using the custom command,
    waits until it is serving, and then yields the base URL.
    After tests complete, the process is terminated.
    """
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"  # disable buffering for immediate output
    env["STREAMLIT_SERVER_HEADLESS"] = "true"  # ensure headless mode in CI

    process = subprocess.Popen(
        ["run_t3co_go"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        env=env,
    )

    port = None
    start_time = time.time()

    # Increase timeout to 60 seconds in case GitHub Actions is slower
    while time.time() - start_time < 60:
        line = process.stdout.readline()
        if not line:
            time.sleep(0.1)
            continue
        # Match lines like "Local URL:" or "Network URL:" with either localhost or 127.0.0.1
        match = re.search(
            r"(?:Local|Network) URL:\s+http://(?:localhost|127\.0\.0\.1):(\d+)", line
        )
        if match:
            port = int(match.group(1))
            break

    if port is None:
        process.terminate()
        pytest.fail("Streamlit app did not start within timeout.")

    base_url = f"http://localhost:{port}"
    yield base_url

    process.terminate()
    process.wait(timeout=5)


def test_app_responds(streamlit_app):
    """
    Test that the app responds to a GET request on its base URL.
    """
    response = requests.get(streamlit_app)
    assert response.status_code == 200
    expected_texts = ["Streamlit", "T3Co", "t3co_go"]
    assert any(text in response.text for text in expected_texts)
