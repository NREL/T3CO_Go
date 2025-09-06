def load_vehicle_data(file_path):
    import pandas as pd
    try:
        data = pd.read_csv(file_path)
        return data
    except Exception as e:
        raise ValueError(f"Error loading vehicle data: {e}")

def load_scenario_data(file_path):
    import pandas as pd
    try:
        data = pd.read_csv(file_path)
        return data
    except Exception as e:
        raise ValueError(f"Error loading scenario data: {e}")

def validate_inputs(vehicle_data, scenario_data):
    if vehicle_data.empty or scenario_data.empty:
        raise ValueError("Vehicle data or scenario data cannot be empty.")
    # Additional validation logic can be added here

def calculate_tco(vehicle_data, scenario_data):
    # Placeholder for TCO calculation logic
    tco_results = {}
    # Perform calculations based on vehicle_data and scenario_data
    return tco_results

def save_results_to_file(results, output_path):
    import json
    try:
        with open(output_path, 'w') as f:
            json.dump(results, f)
    except Exception as e:
        raise ValueError(f"Error saving results to file: {e}")