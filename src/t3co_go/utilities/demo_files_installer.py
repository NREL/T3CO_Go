from t3co.utilities.demo_inputs_installer import copy_demo_input_files


def main():
    """
    This function requests user inputs for whether and where to copy T3CO demo input files from the t3co.resources folder. It then calls the copy_demo_input_files function.
    """
    copy_demo_input_files(".")
