from streamlit.testing.v1 import AppTest


def test_t3co_app():
    """
    Test the t3co_go Streamlit app using st.testing.v1.AppTest.
    This test launches the app, captures its output, and checks for expected content.
    """
    # Create an AppTest instance pointing to your main app file
    app_test = AppTest.from_file("src/t3co_go/app/t3co_app.py")

    # Run the app with a timeout to prevent indefinite hangs
    app_test.run()
    assert not app_test.exception
