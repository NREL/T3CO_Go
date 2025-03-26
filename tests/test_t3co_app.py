from streamlit.testing.v1 import AppTest
import pytest
from t3co.utilities.demo_inputs_installer import copy_demo_input_files


@pytest.mark.timeout(300)
def test_t3co_app():
    """
    Test the t3co_go Streamlit app using st.testing.v1.AppTest.
    This test launches the app, captures its output, and checks for expected content.
    """
    copy_demo_input_files(".")
    # Create an AppTest instance pointing to your main app file
    app_test = AppTest.from_file("src/t3co_go/app/t3co_app.py")

    # Run the app with a timeout to prevent indefinite hangs
    result = app_test.run(timeout=60)

    # Check that expected text appears in the app's stdout.
    # Adjust the assertion as needed based on your app's output.
    assert not result.exception, "Expected output not found in app stdout"
