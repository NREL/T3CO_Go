from django.conf import settings
import os
import json
import pandas as pd
from pathlib import Path
import sys
import importlib.util

# Add the T3CO source to the path to import existing modules
t3co_go_src_path = Path(__file__).parents[3] / "src"
t3co_2_0_path = Path(__file__).parents[3] / "t3co-2.0"
sys.path.insert(0, str(t3co_go_src_path))
sys.path.insert(0, str(t3co_2_0_path))

# Initialize variables for T3CO modules
t3co_run_module = None
t3co_sweep_module = None

try:
    # Try to import T3CO 2.0 from local subtree first
    sys.path.insert(0, str(t3co_2_0_path))
    t3co_run_spec = importlib.util.find_spec("t3co.run")
    t3co_sweep_spec = importlib.util.find_spec("t3co.sweep")

    if t3co_run_spec and t3co_sweep_spec:
        t3co_run_module = importlib.util.module_from_spec(t3co_run_spec)
        t3co_sweep_module = importlib.util.module_from_spec(t3co_sweep_spec)
        T3CO_VERSION = "2.0"
        print("Successfully found T3CO 2.0 from local subtree")
    else:
        raise ImportError("T3CO 2.0 modules not found in subtree")
except ImportError as e:
    print(f"T3CO 2.0 subtree import failed: {e}")
    try:
        # Fallback to pip installation
        t3co_run_spec = importlib.util.find_spec("t3co.run")
        t3co_sweep_spec = importlib.util.find_spec("t3co.sweep")

        if t3co_run_spec and t3co_sweep_spec:
            t3co_run_module = importlib.util.module_from_spec(t3co_run_spec)
            t3co_sweep_module = importlib.util.module_from_spec(t3co_sweep_spec)
            T3CO_VERSION = "2.0"
            print("Successfully found T3CO 2.0 from pip")
        else:
            raise ImportError("T3CO 2.0 modules not found via pip")
    except ImportError as e:
        print(f"T3CO 2.0 pip import failed: {e}")
        try:
            # Fallback to local T3CO_Go modules
            t3co_go_spec = importlib.util.find_spec("t3co_go.run.run_t3co")
            if t3co_go_spec:
                from t3co_go.run.run_t3co import run_t3co

                T3CO_VERSION = "1.0"
                print("Using local T3CO_Go modules")
            else:
                raise ImportError("T3CO_Go modules not found")
        except ImportError:
            print(
                "Warning: Neither T3CO 2.0 nor local T3CO_Go modules could be imported"
            )
            T3CO_VERSION = "none"


class T3COIntegration:
    def __init__(self):
        self.vehicle_data_path = os.path.join(
            settings.BASE_DIR, "demo_inputs", "vehicles"
        )
        self.scenario_data_path = os.path.join(
            settings.BASE_DIR, "demo_inputs", "scenarios"
        )
        self.config_data_path = os.path.join(settings.BASE_DIR, "demo_inputs")
        self.results_path = os.path.join(settings.MEDIA_ROOT, "results")

        # Ensure directories exist
        os.makedirs(self.vehicle_data_path, exist_ok=True)
        os.makedirs(self.scenario_data_path, exist_ok=True)
        os.makedirs(self.config_data_path, exist_ok=True)
        os.makedirs(self.results_path, exist_ok=True)

        # Setup demo data
        self._setup_demo_data()

    def _setup_demo_data(self):
        """Setup demo data for T3CO analysis"""
        try:
            vehicles_dir = Path(self.vehicle_data_path)
            if not vehicles_dir.exists() or not list(vehicles_dir.glob("*.csv")):
                print("Setting up demo data...")
                if T3CO_VERSION == "2.0":
                    self._setup_demo_data_v2()
                else:
                    self._create_basic_demo_data()
                print("Demo data setup complete!")
        except Exception as e:
            print(f"Warning: Could not setup demo data: {e}")
            self._create_basic_demo_data()

    def _setup_demo_data_v2(self):
        """Setup demo data compatible with T3CO 2.0 structure"""
        try:
            # Create basic demo vehicles for T3CO 2.0
            demo_vehicles = {
                "bev_sedan.json": {
                    "vehicle_type": "BEV",
                    "scenario_name": "default",
                    "vehicle_attributes": {
                        "name": "BEV Sedan",
                        "veh_kg": 1800,
                        "veh_life_mi": 150000,
                        "purchase_cost": 45000,
                        "battery_kwh": 75,
                        "motor_kw": 200,
                        "combined_mpge": 120,
                    },
                    "economic_attributes": {
                        "discount_rate": 0.07,
                        "insurance_rate": 0.015,
                        "maintenance_cost_per_mile": 0.04,
                    },
                },
                "ice_sedan.json": {
                    "vehicle_type": "ICE",
                    "scenario_name": "default",
                    "vehicle_attributes": {
                        "name": "ICE Sedan",
                        "veh_kg": 1600,
                        "veh_life_mi": 150000,
                        "purchase_cost": 30000,
                        "engine_kw": 150,
                        "combined_mpg": 30,
                    },
                    "economic_attributes": {
                        "discount_rate": 0.07,
                        "insurance_rate": 0.015,
                        "maintenance_cost_per_mile": 0.06,
                    },
                },
            }

            for filename, vehicle_data in demo_vehicles.items():
                vehicle_file = os.path.join(self.vehicle_data_path, filename)
                with open(vehicle_file, "w") as f:
                    json.dump(vehicle_data, f, indent=2)

            # Create basic demo scenarios
            demo_scenarios = {
                "default.json": {
                    "scenario_name": "default",
                    "analysis_years": 10,
                    "annual_miles": 12000,
                    "fuel_prices": {
                        "electricity_price_per_kwh": 0.12,
                        "gasoline_price_per_gal": 3.50,
                        "diesel_price_per_gal": 3.80,
                    },
                    "economic_scenario": {
                        "discount_rate": 0.07,
                        "escalation_rate": 0.025,
                    },
                }
            }

            for filename, scenario_data in demo_scenarios.items():
                scenario_file = os.path.join(self.scenario_data_path, filename)
                with open(scenario_file, "w") as f:
                    json.dump(scenario_data, f, indent=2)

        except Exception as e:
            print(f"Warning: Could not setup T3CO 2.0 demo data: {e}")

    def _create_basic_demo_data(self):
        """Create basic demo data if T3CO not available"""
        # Basic CSV vehicle data
        basic_vehicle_csv = """vehicle_type,purchase_cost,fuel_efficiency,annual_miles,vehicle_life_mi
BEV,45000,120,12000,150000
ICE,30000,30,12000,150000"""

        vehicle_file = os.path.join(self.vehicle_data_path, "basic_demo.csv")
        with open(vehicle_file, "w") as f:
            f.write(basic_vehicle_csv)

        # Basic CSV scenario data
        basic_scenario_csv = """scenario_name,electricity_price,gasoline_price,discount_rate
default,0.12,3.50,0.07"""

        scenario_file = os.path.join(self.scenario_data_path, "default.csv")
        with open(scenario_file, "w") as f:
            f.write(basic_scenario_csv)

    def load_vehicle_data(self, filename):
        """Load vehicle data - supports both JSON and CSV"""
        file_path = os.path.join(self.vehicle_data_path, filename)

        if filename.endswith(".json"):
            with open(file_path, "r") as file:
                return json.load(file)
        elif filename.endswith(".csv"):
            return pd.read_csv(file_path)
        else:
            raise ValueError(f"Unsupported file format: {filename}")

    def load_scenario_data(self, filename):
        """Load scenario data - supports both JSON and CSV"""
        file_path = os.path.join(self.scenario_data_path, filename)

        if filename.endswith(".json"):
            with open(file_path, "r") as file:
                return json.load(file)
        elif filename.endswith(".csv"):
            return pd.read_csv(file_path)
        else:
            raise ValueError(f"Unsupported file format: {filename}")

    def perform_tco_analysis(self, vehicle_file, scenario_file, analysis_params=None):
        """
        Perform TCO analysis using available T3CO version

        Args:
            vehicle_file (str): Path to vehicle file
            scenario_file (str): Path to scenario file
            analysis_params (dict): Optional analysis parameters

        Returns:
            dict: Analysis results with total costs, breakdowns, and detailed data
        """
        try:
            print(f"Running T3CO analysis: {vehicle_file} + {scenario_file}")

            # Load vehicle and scenario data
            vehicle_data = self.load_vehicle_data(vehicle_file)
            scenario_data = self.load_scenario_data(scenario_file)

            if T3CO_VERSION == "2.0":
                results = self._run_t3co_v2_analysis(
                    vehicle_data, scenario_data, analysis_params
                )
            else:
                results = self._run_t3co_v1_analysis(
                    vehicle_data, scenario_data, analysis_params
                )

            # Process and return results
            processed_results = self._process_results(results)
            processed_results["success"] = True

            return processed_results

        except Exception as e:
            print(f"T3CO analysis error: {e}")
            import traceback

            traceback.print_exc()

            return {
                "success": False,
                "error": str(e),
                "total_cost": 0,
                "cost_per_mile": 0,
                "annual_cost": 0,
                "cost_breakdown": {},
                "details": {},
                "raw_results": [],
            }

    def _run_t3co_v2_analysis(self, vehicle_data, scenario_data, analysis_params):
        """Run T3CO 2.0 analysis"""
        # For now, implement basic calculation until T3CO 2.0 is fully integrated
        return self._calculate_basic_tco(vehicle_data, scenario_data, analysis_params)

    def _run_t3co_v1_analysis(self, vehicle_data, scenario_data, analysis_params):
        """Run T3CO 1.0 analysis"""
        try:
            # Create temporary config file for T3CO
            config_path = self._create_t3co_config(
                vehicle_data, scenario_data, analysis_params
            )

            # Run T3CO analysis
            results_df = run_t3co(
                analysis_id=1,
                config_filename=config_path,
                run_multi=False,
                save_results=True,
            )

            return results_df.to_dict("records")[0] if not results_df.empty else {}

        except Exception as e:
            print(f"T3CO v1 analysis failed: {e}")
            return self._calculate_basic_tco(
                vehicle_data, scenario_data, analysis_params
            )

    def _calculate_basic_tco(self, vehicle_data, scenario_data, analysis_params=None):
        """Basic TCO calculation"""
        try:
            # Extract vehicle parameters
            if isinstance(vehicle_data, dict):
                if "vehicle_attributes" in vehicle_data:
                    # T3CO 2.0 format
                    attrs = vehicle_data["vehicle_attributes"]
                    purchase_cost = attrs.get("purchase_cost", 35000)
                    fuel_efficiency = attrs.get(
                        "combined_mpge", attrs.get("combined_mpg", 100)
                    )
                else:
                    # Legacy format
                    purchase_cost = vehicle_data.get("purchase_cost", 35000)
                    fuel_efficiency = vehicle_data.get("fuel_efficiency", 100)
            else:
                # DataFrame
                purchase_cost = vehicle_data.get("purchase_cost", [35000]).iloc[0]
                fuel_efficiency = vehicle_data.get("fuel_efficiency", [100]).iloc[0]

            # Extract scenario parameters
            if isinstance(scenario_data, dict):
                if "fuel_prices" in scenario_data:
                    # T3CO 2.0 format
                    annual_miles = scenario_data.get("annual_miles", 12000)
                    fuel_price = scenario_data["fuel_prices"].get(
                        "electricity_price_per_kwh",
                        scenario_data["fuel_prices"].get(
                            "gasoline_price_per_gal", 3.50
                        ),
                    )
                else:
                    # Legacy format
                    annual_miles = scenario_data.get("annual_miles", 12000)
                    fuel_price = scenario_data.get(
                        "electricity_price", scenario_data.get("gasoline_price", 3.50)
                    )
            else:
                # DataFrame
                annual_miles = scenario_data.get("annual_miles", [12000]).iloc[0]
                fuel_price = scenario_data.get(
                    "electricity_price", scenario_data.get("gasoline_price", [3.50])
                ).iloc[0]

            # Apply analysis parameters
            if analysis_params:
                annual_miles = analysis_params.get("annual_miles", annual_miles)
                analysis_years = analysis_params.get("analysis_years", 10)
            else:
                analysis_years = 10

            # Calculate costs
            vehicle_life_miles = annual_miles * analysis_years
            fuel_units_needed = vehicle_life_miles / fuel_efficiency
            total_fuel_cost = fuel_units_needed * fuel_price
            maintenance_per_mile = 0.05
            total_maintenance_cost = vehicle_life_miles * maintenance_per_mile
            insurance_cost = purchase_cost * 0.015 * analysis_years

            total_cost = (
                purchase_cost
                + total_fuel_cost
                + total_maintenance_cost
                + insurance_cost
            )
            cost_per_mile = total_cost / vehicle_life_miles
            annual_cost = total_cost / analysis_years

            return {
                "total_cost_of_ownership": total_cost,
                "cost_per_mile": cost_per_mile,
                "annual_cost": annual_cost,
                "purchase_cost": purchase_cost,
                "fuel_cost": total_fuel_cost,
                "maintenance_cost": total_maintenance_cost,
                "insurance_cost": insurance_cost,
                "vehicle_life_years": analysis_years,
                "fuel_efficiency": fuel_efficiency,
                "annual_miles": annual_miles,
            }

        except Exception as e:
            print(f"Basic TCO calculation failed: {e}")
            return {"total_cost_of_ownership": 0, "cost_per_mile": 0, "annual_cost": 0}

    def _create_t3co_config(self, vehicle_data, scenario_data, analysis_params):
        """Create T3CO configuration file"""
        # This would create a proper T3CO config file
        # For now, return a placeholder
        return os.path.join(self.config_data_path, "temp_config.csv")

    def _process_results(self, results):
        """Process results into standardized format"""
        total_cost = results.get("total_cost_of_ownership", 0)
        cost_per_mile = results.get("cost_per_mile", 0)
        annual_cost = results.get("annual_cost", 0)

        cost_breakdown = {
            "purchase_cost": results.get("purchase_cost", 0),
            "fuel_cost": results.get("fuel_cost", 0),
            "maintenance_cost": results.get("maintenance_cost", 0),
            "insurance_cost": results.get("insurance_cost", 0),
        }

        summary = "T3CO Analysis Results\n"
        summary += f"Total Cost of Ownership: ${total_cost:,.2f}\n"
        summary += f"Cost per Mile: ${cost_per_mile:.3f}\n"
        summary += f"Annual Cost: ${annual_cost:,.2f}\n"

        return {
            "total_cost": float(total_cost),
            "cost_per_mile": float(cost_per_mile),
            "annual_cost": float(annual_cost),
            "cost_breakdown": cost_breakdown,
            "details": results,
            "raw_results": results,
            "summary": summary,
            "analysis_count": 1,
            "t3co_version": T3CO_VERSION,
        }

    def get_available_vehicles(self):
        """Get list of available vehicle files"""
        vehicles_dir = Path(self.vehicle_data_path)
        if vehicles_dir.exists():
            vehicle_files = []
            for ext in ["*.json", "*.csv"]:
                vehicle_files.extend([f.name for f in vehicles_dir.glob(ext)])
            return sorted(vehicle_files)
        return []

    def get_available_scenarios(self):
        """Get list of available scenario files"""
        scenarios_dir = Path(self.scenario_data_path)
        if scenarios_dir.exists():
            scenario_files = []
            for ext in ["*.json", "*.csv"]:
                scenario_files.extend([f.name for f in scenarios_dir.glob(ext)])
            return sorted(scenario_files)
        return []

    def save_results(self, results, output_filename):
        """Save analysis results to file"""
        output_path = os.path.join(self.results_path, output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w") as file:
            json.dump(results, file, indent=2, default=str)

        return output_path

    def perform_parameter_based_analysis(self, form_data):
        """
        Perform TCO analysis using form parameters instead of files
        
        Args:
            form_data (dict): Form data with vehicle and scenario parameters
            
        Returns:
            dict: Analysis results
        """
        try:
            # Create vehicle configuration from parameters
            vehicle_config = self._create_vehicle_config_from_params(form_data)
            
            # Create scenario configuration from parameters  
            scenario_config = self._create_scenario_config_from_params(form_data)
            
            # Perform analysis with generated configs
            results = self._calculate_parameter_based_tco(vehicle_config, scenario_config, form_data)
            
            # Process results
            processed_results = self._process_results(results)
            processed_results["success"] = True
            
            return processed_results
            
        except Exception as e:
            print(f"Parameter-based analysis error: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "success": False,
                "error": str(e),
                "total_cost": 0,
                "cost_per_mile": 0,
                "annual_cost": 0,
                "cost_breakdown": {},
                "details": {},
            }
    
    def _create_vehicle_config_from_params(self, form_data):
        """Create vehicle configuration from form parameters"""
        try:
            # Load baseline vehicle data for the selected year
            # Get demo_inputs path - should be relative to the main project root
            main_project_root = settings.BASE_DIR.parent.parent
            demo_inputs_path = os.path.join(main_project_root, 'demo_inputs')
            baseline_path = os.path.join(demo_inputs_path, 'auxiliary', 'BaselineVehicle.csv')
            
            if os.path.exists(baseline_path):
                df = pd.read_csv(baseline_path)
                year = int(form_data.get('analysis_year', 2025))
                baseline_row = df[df['Year'] == year]
                
                if not baseline_row.empty:
                    baseline_data = baseline_row.iloc[0].to_dict()
                else:
                    baseline_data = df.iloc[0].to_dict()  # Fallback to first row
            else:
                baseline_data = {}
            
            # Override with form parameters
            vehicle_config = {
                'Year': int(form_data.get('analysis_year', 2025)),
                'dragCoef': float(form_data.get('drag_coefficient', 0.546)),
                'frontalAreaM2': float(form_data.get('frontal_area_m2', 10.18)),
                'gliderKg': float(form_data.get('glider_kg', 11776)),
                'vehicle_type': form_data.get('vehicle_type', 'Class8_long_haul'),
                **baseline_data  # Include all baseline parameters
            }
            
            return vehicle_config
            
        except Exception as e:
            print(f"Error creating vehicle config: {e}")
            return {
                'Year': 2025,
                'dragCoef': 0.546,
                'frontalAreaM2': 10.18,
                'gliderKg': 11776,
                'vehicle_type': 'Class8_long_haul'
            }
    
    def _create_scenario_config_from_params(self, form_data):
        """Create scenario configuration from form parameters"""
        try:
            # Load vocation requirements for the selected vocation and year
            # Get demo_inputs path - should be relative to the main project root  
            main_project_root = settings.BASE_DIR.parent.parent
            demo_inputs_path = os.path.join(main_project_root, 'demo_inputs')
            vocation_path = os.path.join(demo_inputs_path, 'auxiliary', 'VocationRequirements.csv')
            
            if os.path.exists(vocation_path):
                df = pd.read_csv(vocation_path)
                year = int(form_data.get('analysis_year', 2025))
                vocation = form_data.get('vocation', 'Long haul')
                
                vocation_row = df[(df['Year'] == year) & (df['vocation'] == vocation)]
                
                if not vocation_row.empty:
                    vocation_data = vocation_row.iloc[0].to_dict()
                else:
                    vocation_data = df.iloc[0].to_dict()  # Fallback
            else:
                vocation_data = {}
            
            # Load fuel prices for the selected region and year
            fuel_prices = self._get_fuel_prices(form_data.get('region', 'Pacific'), int(form_data.get('analysis_year', 2025)))
            
            # Create scenario config
            scenario_config = {
                'vocation': form_data.get('vocation', 'Long haul'),
                'region': form_data.get('region', 'Pacific'),
                'Year': int(form_data.get('analysis_year', 2025)),
                'cargoKg': float(form_data.get('cargo_kg', 16329)),
                'MinRangeMiles': float(form_data.get('min_range_miles', 750)),
                'discount_rate_pct': float(form_data.get('discount_rate_pct', 4.1)),
                'vehicle_life_yr': int(form_data.get('vehicle_life_yr', 7)),
                'annual_vmt': float(form_data.get('annual_vmt', 100000)),
                'fuel_prices': fuel_prices,
                **vocation_data  # Include all vocation parameters
            }
            
            return scenario_config
            
        except Exception as e:
            print(f"Error creating scenario config: {e}")
            return {
                'vocation': 'Long haul',
                'region': 'Pacific',
                'Year': 2025,
                'cargoKg': 16329,
                'MinRangeMiles': 750,
                'discount_rate_pct': 4.1,
                'vehicle_life_yr': 7,
                'annual_vmt': 100000,
                'fuel_prices': {'diesel': 4.0, 'electricity': 0.15}
            }
    
    def _get_fuel_prices(self, region, year):
        """Get fuel prices for the specified region and year"""
        try:
            # Get demo_inputs path - should be relative to the main project root
            main_project_root = settings.BASE_DIR.parent.parent
            demo_inputs_path = os.path.join(main_project_root, 'demo_inputs')
            fuel_path = os.path.join(demo_inputs_path, 'auxiliary', 'FuelPrices.csv')
            
            if os.path.exists(fuel_path):
                df = pd.read_csv(fuel_path)
                region_data = df[df['Region'] == region]
                
                if not region_data.empty:
                    year_col = str(year) if str(year) in df.columns else '2025'
                    
                    fuel_prices = {}
                    for fuel_type in ['gasolineDolPerGal', 'dieselDolPerGal', 'CNGDolPerGge', 'dolPerKwh', 'hydrogenDolPerGGE']:
                        fuel_row = region_data[region_data['Fuel'] == fuel_type.replace('DolPer', '').replace('dolPer', '')]
                        if not fuel_row.empty and year_col in fuel_row.columns:
                            fuel_prices[fuel_type] = float(fuel_row[year_col].iloc[0])
                    
                    return fuel_prices
            
            # Fallback prices
            return {
                'gasolineDolPerGal': 3.50,
                'dieselDolPerGal': 4.00,
                'CNGDolPerGge': 2.00,
                'dolPerKwh': 0.15,
                'hydrogenDolPerGGE': 6.00
            }
            
        except Exception as e:
            print(f"Error getting fuel prices: {e}")
            return {
                'gasolineDolPerGal': 3.50,
                'dieselDolPerGal': 4.00,
                'CNGDolPerGge': 2.00,
                'dolPerKwh': 0.15,
                'hydrogenDolPerGGE': 6.00
            }
    
    def _calculate_parameter_based_tco(self, vehicle_config, scenario_config, form_data):
        """Calculate TCO using parameter-based configurations"""
        try:
            # Extract key parameters
            analysis_years = int(scenario_config.get('vehicle_life_yr', 7))
            annual_miles = float(scenario_config.get('annual_vmt', 100000))
            
            # Vehicle costs
            base_vehicle_cost = vehicle_config.get('vehicle_glider_cost_dol', 121919)
            
            # Fuel efficiency estimate based on drag coefficient and frontal area
            drag_coef = float(vehicle_config.get('dragCoef', 0.546))
            frontal_area = float(vehicle_config.get('frontalAreaM2', 10.18))
            
            # Simple fuel efficiency model (higher drag = lower efficiency)
            base_mpg = 7.0  # Base MPG for Class 8 truck
            aero_factor = (0.546 / drag_coef) * (10.18 / frontal_area)  # Improvement factor
            fuel_efficiency = base_mpg * aero_factor
            
            # Fuel costs
            fuel_prices = scenario_config.get('fuel_prices', {})
            diesel_price = fuel_prices.get('dieselDolPerGal', 4.0)
            
            # Calculate costs
            total_miles = annual_miles * analysis_years
            total_fuel_gallons = total_miles / fuel_efficiency
            total_fuel_cost = total_fuel_gallons * diesel_price
            
            # Maintenance costs (per mile)
            maintenance_per_mile = 0.15  # $0.15 per mile for Class 8
            total_maintenance_cost = total_miles * maintenance_per_mile
            
            # Insurance (percentage of vehicle value)
            annual_insurance_rate = 0.02  # 2% of vehicle value
            total_insurance_cost = base_vehicle_cost * annual_insurance_rate * analysis_years
            
            # Depreciation
            residual_value_pct = 0.20  # 20% residual value
            depreciation = base_vehicle_cost * (1 - residual_value_pct)
            
            # Registration and licensing
            annual_registration = 2000  # Annual registration fees
            total_registration_cost = annual_registration * analysis_years
            
            # Total costs
            total_cost = (
                base_vehicle_cost + 
                total_fuel_cost + 
                total_maintenance_cost + 
                total_insurance_cost + 
                total_registration_cost
            )
            
            cost_per_mile = total_cost / total_miles
            annual_cost = total_cost / analysis_years
            
            return {
                'total_cost_of_ownership': total_cost,
                'cost_per_mile': cost_per_mile,
                'annual_cost': annual_cost,
                'purchase_cost': base_vehicle_cost,
                'fuel_cost': total_fuel_cost,
                'maintenance_cost': total_maintenance_cost,
                'insurance_cost': total_insurance_cost,
                'depreciation': depreciation,
                'registration_cost': total_registration_cost,
                'vehicle_life_years': analysis_years,
                'fuel_efficiency': fuel_efficiency,
                'annual_miles': annual_miles,
                'fuel_price': diesel_price,
                'total_miles': total_miles,
                'aero_improvement_factor': aero_factor
            }
            
        except Exception as e:
            print(f"Parameter-based TCO calculation failed: {e}")
            return {
                'total_cost_of_ownership': 0,
                'cost_per_mile': 0,
                'annual_cost': 0,
                'purchase_cost': 0,
                'fuel_cost': 0,
                'maintenance_cost': 0,
                'insurance_cost': 0
            }


# Standalone function for backward compatibility
def perform_tco_analysis(vehicle_file, scenario_file, analysis_params=None):
    """Standalone function wrapper for the T3COIntegration class"""
    integration = T3COIntegration()
    return integration.perform_tco_analysis(
        vehicle_file, scenario_file, analysis_params
    )
