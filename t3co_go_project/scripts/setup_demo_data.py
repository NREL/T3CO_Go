import os
import shutil

def setup_demo_data():
    demo_inputs_dir = '/Users/hpanneer/GitHub/T3CO_Go-Private/demo_inputs'
    vehicles_dir = os.path.join(demo_inputs_dir, 'vehicles')
    scenarios_dir = os.path.join(demo_inputs_dir, 'scenarios')

    # Create directories if they don't exist
    os.makedirs(vehicles_dir, exist_ok=True)
    os.makedirs(scenarios_dir, exist_ok=True)

    # Example: Copy demo vehicle and scenario files from a source directory
    # Replace 'source_vehicles' and 'source_scenarios' with actual source paths
    source_vehicles = '/path/to/source_vehicles'
    source_scenarios = '/path/to/source_scenarios'

    for filename in os.listdir(source_vehicles):
        shutil.copy(os.path.join(source_vehicles, filename), vehicles_dir)

    for filename in os.listdir(source_scenarios):
        shutil.copy(os.path.join(source_scenarios, filename), scenarios_dir)

if __name__ == '__main__':
    setup_demo_data()