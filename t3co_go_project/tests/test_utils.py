from django.test import TestCase
from core.utils import some_utility_function  # Replace with actual utility function names

class UtilsTestCase(TestCase):
    def test_some_utility_function(self):
        # Test the utility function with expected inputs and outputs
        input_data = ...  # Define your input data
        expected_output = ...  # Define the expected output
        self.assertEqual(some_utility_function(input_data), expected_output)

    def test_another_utility_function(self):
        # Test another utility function
        input_data = ...  # Define your input data
        expected_output = ...  # Define the expected output
        self.assertEqual(some_utility_function(input_data), expected_output)

    # Add more test methods as needed for other utility functions