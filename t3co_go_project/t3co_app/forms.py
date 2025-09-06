from django import forms
from django.core.validators import FileExtensionValidator
from django.conf import settings
import os
import pandas as pd


class MultipleFileInput(forms.ClearableFileInput):
    """Custom widget for multiple file uploads."""

    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    """Custom field for multiple file uploads."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class TCOAnalysisForm(forms.Form):
    """Form for single vehicle TCO analysis."""

    analysis_name = forms.CharField(
        max_length=200,
        label="Analysis Name",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter analysis name"}
        ),
    )

    vehicle_file = forms.FileField(
        label="Vehicle Input File",
        validators=[FileExtensionValidator(allowed_extensions=["json", "csv"])],
        widget=forms.ClearableFileInput(
            attrs={"class": "form-control", "accept": ".json,.csv"}
        ),
        help_text="Upload vehicle configuration file (JSON for T3CO 2.0, CSV for legacy)",
    )

    scenario_file = forms.FileField(
        label="Scenario Input File",
        validators=[FileExtensionValidator(allowed_extensions=["json", "csv"])],
        widget=forms.ClearableFileInput(
            attrs={"class": "form-control", "accept": ".json,.csv"}
        ),
        help_text="Upload scenario configuration file (JSON for T3CO 2.0, CSV for legacy)",
    )

    analysis_parameters = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Additional analysis parameters (optional)",
            }
        ),
        label="Analysis Parameters",
        required=False,
        help_text="Optional JSON parameters to override default analysis settings",
    )


class TCOAnalysisParameterForm(forms.Form):
    """Form for TCO analysis using dropdown parameter selections"""

    # Analysis identification
    analysis_name = forms.CharField(
        max_length=100,
        label="Analysis Name",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter analysis name"}
        ),
    )

    # Vehicle selection components parsed from scenario_name
    vehicle_class = forms.ChoiceField(
        label="Vehicle Class",
        choices=[],
        widget=forms.Select(attrs={"class": ""}),
    )

    cab_type = forms.ChoiceField(
        label="Cab Type",
        choices=[],
        widget=forms.Select(attrs={"class": ""}),
    )

    roof_type = forms.ChoiceField(
        label="Roof Type",
        choices=[],
        widget=forms.Select(attrs={"class": ""}),
    )

    fuel_type = forms.ChoiceField(
        label="Fuel Type",
        choices=[],
        widget=forms.Select(attrs={"class": ""}),
    )

    # Analysis year
    analysis_year = forms.ChoiceField(
        label="Analysis Year",
        choices=[],
        widget=forms.Select(attrs={"class": ""}),
    )

    program_status = forms.ChoiceField(
        label="Program Status",
        choices=[],
        widget=forms.Select(attrs={"class": ""}),
    )

    # Scenario/vocation
    vocation = forms.ChoiceField(
        label="Vocation",
        choices=[],
        widget=forms.Select(attrs={"class": ""}),
    )

    # Region for fuel prices
    region = forms.ChoiceField(
        label="Region",
        choices=[],
        widget=forms.Select(attrs={"class": ""}),
    )

    # Key adjustable parameters with enhanced widgets
    drag_coefficient = forms.FloatField(
        label="Drag Coefficient",
        min_value=0.1,
        max_value=2.0,
        widget=forms.NumberInput(
            attrs={
                "class": "validate range-input",
                "step": "0.001",
                "data-slider": "true",
                "data-min": "0.1",
                "data-max": "2.0",
                "data-step": "0.001",
            }
        ),
    )

    frontal_area_m2 = forms.FloatField(
        label="Frontal Area (m²)",
        min_value=5.0,
        max_value=20.0,
        widget=forms.NumberInput(
            attrs={
                "class": "validate range-input",
                "step": "0.1",
                "data-slider": "true",
                "data-min": "5.0",
                "data-max": "20.0",
                "data-step": "0.1",
            }
        ),
    )

    glider_kg = forms.FloatField(
        label="Glider Weight (kg)",
        min_value=5000,
        max_value=25000,
        widget=forms.NumberInput(
            attrs={
                "class": "validate range-input",
                "data-slider": "true",
                "data-min": "5000",
                "data-max": "25000",
                "data-step": "100",
            }
        ),
    )

    cargo_kg = forms.FloatField(
        label="Cargo Weight (kg)",
        min_value=5000,
        max_value=35000,
        widget=forms.NumberInput(
            attrs={
                "class": "validate range-input",
                "data-slider": "true",
                "data-min": "5000",
                "data-max": "35000",
                "data-step": "100",
            }
        ),
    )

    min_range_miles = forms.FloatField(
        label="Minimum Range (miles)",
        min_value=100,
        max_value=1500,
        widget=forms.NumberInput(
            attrs={
                "class": "validate range-input",
                "data-slider": "true",
                "data-min": "100",
                "data-max": "1500",
                "data-step": "25",
            }
        ),
    )

    # Economic parameters with sliders
    discount_rate_pct = forms.FloatField(
        label="Discount Rate (%)",
        initial=4.1,
        min_value=0.0,
        max_value=15.0,
        widget=forms.NumberInput(
            attrs={
                "class": "validate range-input",
                "step": "0.01",
                "data-slider": "true",
                "data-min": "0.0",
                "data-max": "15.0",
                "data-step": "0.01",
            }
        ),
    )

    vehicle_life_yr = forms.IntegerField(
        label="Vehicle Life (years)",
        initial=7,
        min_value=3,
        max_value=20,
        widget=forms.NumberInput(
            attrs={
                "class": "validate range-input",
                "data-slider": "true",
                "data-min": "3",
                "data-max": "20",
                "data-step": "1",
            }
        ),
    )

    annual_vmt = forms.FloatField(
        label="Annual VMT",
        initial=100000,
        min_value=20000,
        max_value=200000,
        widget=forms.NumberInput(
            attrs={
                "class": "validate range-input",
                "data-slider": "true",
                "data-min": "20000",
                "data-max": "200000",
                "data-step": "5000",
            }
        ),
    )

    # Cost component toggles
    include_purchase_cost = forms.BooleanField(
        label="Include Purchase Cost",
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "filled-in cost-toggle"}),
    )

    include_fuel_cost = forms.BooleanField(
        label="Include Fuel Cost",
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "filled-in cost-toggle"}),
    )

    include_maintenance_cost = forms.BooleanField(
        label="Include Maintenance Cost",
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "filled-in cost-toggle"}),
    )

    include_insurance_cost = forms.BooleanField(
        label="Include Insurance Cost",
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "filled-in cost-toggle"}),
    )

    include_registration_cost = forms.BooleanField(
        label="Include Registration/Licensing",
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "filled-in cost-toggle"}),
    )

    include_depreciation = forms.BooleanField(
        label="Include Depreciation",
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "filled-in cost-toggle"}),
    )

    # Analysis options checkboxes
    enable_sensitivity_analysis = forms.BooleanField(
        label="Enable Sensitivity Analysis",
        initial=False,
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "filled-in analysis-option"}),
    )

    enable_monte_carlo = forms.BooleanField(
        label="Enable Monte Carlo Simulation",
        initial=False,
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "filled-in analysis-option"}),
    )

    real_time_update = forms.BooleanField(
        label="Real-time Parameter Updates",
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "filled-in ui-option"}),
    )

    def __init__(self, *args, **kwargs):
        print("=== TCOAnalysisParameterForm __init__ called ===")
        print(f"Working directory: {os.getcwd()}")
        super().__init__(*args, **kwargs)
        print("About to call _populate_choices...")
        self._populate_choices()
        print("About to call _set_initial_values...")
        self._set_initial_values()
        print("=== End form initialization ===\n")

    def _parse_scenario_name(self, scenario_name):
        """Parse vehicle scenario_name into components"""
        import re

        components = {
            "vehicle_class": "Unknown",
            "cab_type": "Unknown",
            "roof_type": "Unknown",
            "fuel_type": "Unknown",
            "year": "Unknown",
            "program_status": "Unknown",
        }

        try:
            # Pattern: "Class X [cab_type] [roof_type] roof (fuel_type, year, program_status)"
            # Example: "Class 8 Sleeper cab high roof (Diesel, 2025, no program)"

            # Extract vehicle class (Class 8, Class 6, etc.)
            class_match = re.search(r"Class\s+(\d+)", scenario_name)
            if class_match:
                components["vehicle_class"] = f"Class {class_match.group(1)}"

            # Extract cab type (between "Class X" and "roof")
            cab_match = re.search(r"Class\s+\d+\s+(.+?)\s+roof", scenario_name)
            if cab_match:
                cab_parts = cab_match.group(1).strip().split()
                if len(cab_parts) >= 2:
                    components["cab_type"] = " ".join(
                        cab_parts[:-1]
                    )  # Everything except the last word
                    components["roof_type"] = cab_parts[
                        -1
                    ]  # The last word (high, mid, low)
                elif len(cab_parts) == 1:
                    components["roof_type"] = cab_parts[0]

            # Extract content in parentheses: (fuel_type, year, program_status)
            paren_match = re.search(r"\(([^)]+)\)", scenario_name)
            if paren_match:
                paren_content = paren_match.group(1)
                parts = [part.strip() for part in paren_content.split(",")]

                if len(parts) >= 3:
                    components["fuel_type"] = parts[0]
                    components["year"] = parts[1]
                    components["program_status"] = parts[2]
                elif len(parts) == 2:
                    components["fuel_type"] = parts[0]
                    components["year"] = parts[1]
                elif len(parts) == 1:
                    # Try to detect if it's a year
                    if parts[0].isdigit():
                        components["year"] = parts[0]
                    else:
                        components["fuel_type"] = parts[0]

        except Exception as e:
            print(f"Error parsing scenario_name '{scenario_name}': {e}")

        return components

    def _populate_choices(self):
        """Populate form choices from actual T3CO demo data"""
        print("  --> _populate_choices method called")
        try:
            # Get demo_inputs path - should be relative to the main project root
            main_project_root = settings.BASE_DIR.parent
            demo_path = os.path.join(main_project_root, "demo_inputs", "inputs")
            print(f"  --> main_project_root: {main_project_root}")
            print(f"  --> demo_path: {demo_path}")

            vehicle_file = os.path.join(
                demo_path, "Demo_FY22_vehicle_model_assumptions.csv"
            )
            print(f"  --> vehicle_file: {vehicle_file}")
            print(f"  --> vehicle_file exists: {os.path.exists(vehicle_file)}")
            scenario_file = os.path.join(
                demo_path, "Demo_FY22_scenario_assumptions.csv"
            )

            # Load vehicle data for choices
            if os.path.exists(vehicle_file):
                vehicle_df = pd.read_csv(vehicle_file)

                # Parse all scenario names to extract components
                parsed_data = []
                for scenario_name in vehicle_df["scenario_name"].unique():
                    components = self._parse_scenario_name(scenario_name)
                    components["original_scenario_name"] = scenario_name
                    parsed_data.append(components)

                # Create choices for each component
                vehicle_classes = sorted(
                    set(
                        item["vehicle_class"]
                        for item in parsed_data
                        if item["vehicle_class"] != "Unknown"
                    )
                )
                cab_types = sorted(
                    set(
                        item["cab_type"]
                        for item in parsed_data
                        if item["cab_type"] != "Unknown"
                    )
                )
                roof_types = sorted(
                    set(
                        item["roof_type"]
                        for item in parsed_data
                        if item["roof_type"] != "Unknown"
                    )
                )
                fuel_types = sorted(
                    set(
                        item["fuel_type"]
                        for item in parsed_data
                        if item["fuel_type"] != "Unknown"
                    )
                )
                program_statuses = sorted(
                    set(
                        item["program_status"]
                        for item in parsed_data
                        if item["program_status"] != "Unknown"
                    )
                )

                # Set choices for dropdowns
                self.fields["vehicle_class"].choices = [
                    (vc, vc) for vc in vehicle_classes
                ]
                self.fields["cab_type"].choices = [(ct, ct.title()) for ct in cab_types]
                self.fields["roof_type"].choices = [
                    (rt, rt.title()) for rt in roof_types
                ]
                self.fields["fuel_type"].choices = [(ft, ft) for ft in fuel_types]
                self.fields["program_status"].choices = [
                    (ps, ps.title()) for ps in program_statuses
                ]

                # Get unique years from both parsed data and direct column
                years_from_parsed = set(
                    item["year"]
                    for item in parsed_data
                    if item["year"] != "Unknown" and item["year"].isdigit()
                )
                years_from_column = set(
                    str(year) for year in vehicle_df["veh_year"].unique()
                )
                all_years = sorted(years_from_parsed.union(years_from_column))
                self.fields["analysis_year"].choices = [
                    (year, year) for year in all_years
                ]

            # Load scenario data for choices
            if os.path.exists(scenario_file):
                scenario_df = pd.read_csv(scenario_file)

                # Get unique vocations
                if "vocation" in scenario_df.columns:
                    vocations = sorted(scenario_df["vocation"].unique())
                    vocation_choices = [(v, v.title()) for v in vocations]
                    self.fields["vocation"].choices = vocation_choices

                # Get unique regions
                if "region" in scenario_df.columns:
                    regions = sorted(scenario_df["region"].unique())
                    region_choices = [(r, r) for r in regions]
                    self.fields["region"].choices = region_choices

        except Exception as e:
            print(f"Error populating form choices from demo data: {e}")
            # Set default choices if data loading fails
            self.fields["vehicle_class"].choices = [("Class 8", "Class 8")]
            self.fields["cab_type"].choices = [("Sleeper cab", "Sleeper Cab")]
            self.fields["roof_type"].choices = [
                ("high", "High"),
                ("mid", "Mid"),
                ("low", "Low"),
            ]
            self.fields["fuel_type"].choices = [("Diesel", "Diesel")]
            self.fields["analysis_year"].choices = [
                ("2020", "2020"),
                ("2025", "2025"),
                ("2030", "2030"),
                ("2035", "2035"),
            ]
            self.fields["program_status"].choices = [("no program", "No Program")]
            self.fields["vocation"].choices = [("Long haul", "Long Haul")]
            self.fields["region"].choices = [("FY22NoProgram", "FY22 No Program")]

        # Debug: Print the final choices that were set
        print("  --> Final choices populated:")
        for field_name, field in self.fields.items():
            if hasattr(field, "choices") and field.choices:
                choices_list = list(field.choices)
                print(
                    f"    {field_name}: {len(choices_list)} choices - {choices_list[:3]}{'...' if len(choices_list) > 3 else ''}"
                )
            else:
                print(f"    {field_name}: No choices or not a choice field")
        print("  --> End _populate_choices\n")

    def get_selected_scenario_name(self):
        """Reconstruct the scenario_name from selected dropdown values"""
        if self.is_valid():
            data = self.cleaned_data
            scenario_name = f"{data['vehicle_class']} {data['cab_type']} {data['roof_type']} roof ({data['fuel_type']}, {data['analysis_year']}, {data['program_status']})"
            return scenario_name
        return None

    def _set_initial_values(self):
        """Set initial values for parameters based on actual T3CO demo data"""
        try:
            # Get demo_inputs path - should be relative to the main project root
            main_project_root = settings.BASE_DIR.parent.parent
            demo_path = os.path.join(main_project_root, "demo_inputs", "inputs", "demo")

            vehicle_file = os.path.join(
                demo_path, "Demo_FY22_vehicle_model_assumptions.csv"
            )
            scenario_file = os.path.join(
                demo_path, "Demo_FY22_scenario_assumptions.csv"
            )

            # Load vehicle data for initial values
            if os.path.exists(vehicle_file):
                vehicle_df = pd.read_csv(vehicle_file)
                # Use the first vehicle row as default (Class 8 Sleeper cab high roof, 2020)
                if not vehicle_df.empty:
                    default_vehicle = vehicle_df.iloc[0]

                    self.fields["drag_coefficient"].initial = default_vehicle.get(
                        "drag_coef", 0.546
                    )
                    self.fields["frontal_area_m2"].initial = default_vehicle.get(
                        "frontal_area_m2", 10.4
                    )
                    self.fields["glider_kg"].initial = default_vehicle.get(
                        "glider_kg", 11776
                    )

            # Load scenario data for initial values
            if os.path.exists(scenario_file):
                scenario_df = pd.read_csv(scenario_file)
                if not scenario_df.empty:
                    default_scenario = scenario_df.iloc[0]

                    self.fields["cargo_kg"].initial = default_scenario.get(
                        "cargo_kg", 17236
                    )
                    self.fields["min_range_miles"].initial = default_scenario.get(
                        "target_range_mi", 750
                    )
                    self.fields["discount_rate_pct"].initial = default_scenario.get(
                        "discount_rate_pct_per_yr", 4.1
                    )
                    self.fields["vehicle_life_yr"].initial = default_scenario.get(
                        "vehicle_life_yr", 7
                    )
                    self.fields["annual_vmt"].initial = (
                        default_scenario.get("vmt", "[100000]")
                        .strip("[]")
                        .split(",")[0]
                        if isinstance(default_scenario.get("vmt"), str)
                        else 100000
                    )

        except Exception as e:
            print(f"Error setting initial values from demo data: {e}")
            # Set fallback defaults
            self.fields["drag_coefficient"].initial = 0.546
            self.fields["frontal_area_m2"].initial = 10.4
            self.fields["glider_kg"].initial = 11776
            self.fields["cargo_kg"].initial = 17236
            self.fields["min_range_miles"].initial = 750


class VehicleComparisonForm(forms.Form):
    """Enhanced form for comparing multiple vehicle-scenario combinations with grouping capabilities."""

    comparison_name = forms.CharField(
        max_length=200,
        label="Comparison Name",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter comparison name"}
        ),
    )

    # Vehicle-Scenario Selection Method
    selection_method = forms.ChoiceField(
        choices=[
            ("dropdown", "Use Parameter Dropdowns"),
            ("file_upload", "Upload Vehicle/Scenario Files"),
        ],
        widget=forms.RadioSelect(attrs={"class": "comparison-method"}),
        label="Selection Method",
        initial="dropdown",
        help_text="Choose how to select vehicles and scenarios for comparison",
    )

    # Dropdown-based selection (multiple configurations)
    vehicle_configurations = forms.CharField(
        widget=forms.HiddenInput(),
        label="Vehicle Configurations",
        required=False,
        help_text="JSON data for selected vehicle configurations",
    )

    # File upload fallback
    vehicle_files = MultipleFileField(
        label="Vehicle Files",
        validators=[FileExtensionValidator(allowed_extensions=["json", "csv"])],
        widget=MultipleFileInput(
            attrs={"class": "form-control", "accept": ".json,.csv"}
        ),
        help_text="Upload multiple vehicle files to compare (JSON or CSV format)",
        required=False,
    )

    scenario_files = MultipleFileField(
        label="Scenario Files", 
        validators=[FileExtensionValidator(allowed_extensions=["json", "csv"])],
        widget=MultipleFileInput(
            attrs={"class": "form-control", "accept": ".json,.csv"}
        ),
        help_text="Upload multiple scenario files (JSON or CSV format)",
        required=False,
    )

    # Grouping and Analysis Options
    group_by_primary = forms.ChoiceField(
        choices=[
            ("none", "No Grouping"),
            ("vehicle_class", "Vehicle Weight Class"),
            ("fuel_type", "Fuel Type"),
            ("analysis_year", "Analysis Year"),
            ("program_status", "Technology Progress"),
            ("vocation", "Vehicle Application"),
            ("region", "Geographic Region"),
        ],
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Primary Grouping",
        initial="fuel_type",
        help_text="Primary criterion for grouping comparison results",
    )

    group_by_secondary = forms.ChoiceField(
        choices=[
            ("none", "No Secondary Grouping"),
            ("vehicle_class", "Vehicle Weight Class"),
            ("fuel_type", "Fuel Type"),
            ("analysis_year", "Analysis Year"),
            ("program_status", "Technology Progress"),
            ("vocation", "Vehicle Application"),
            ("region", "Geographic Region"),
        ],
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Secondary Grouping",
        initial="none",
        help_text="Optional secondary grouping for matrix/grid plots",
        required=False,
    )

    # Comparison metrics selection
    comparison_metrics = forms.MultipleChoiceField(
        choices=[
            ("total_cost", "Total Cost of Ownership"),
            ("cost_per_mile", "Cost per Mile"),
            ("fuel_cost", "Fuel Costs"),
            ("maintenance_cost", "Maintenance Costs"),
            ("capital_cost", "Capital Costs"),
            ("operating_cost", "Operating Costs"),
            ("opportunity_cost", "Opportunity Costs"),
            ("fuel_efficiency", "Fuel Efficiency (MPGGE)"),
            ("range_miles", "Vehicle Range"),
            ("payload_capacity", "Payload Impact"),
        ],
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
        label="Comparison Metrics",
        initial=["total_cost", "cost_per_mile", "fuel_efficiency"],
        help_text="Select metrics to compare across vehicle-scenario combinations",
    )

    # Chart type preferences
    chart_type = forms.ChoiceField(
        choices=[
            ("stacked_bar", "Stacked Bar Chart"),
            ("grouped_bar", "Grouped Bar Chart"),
            ("line_chart", "Line Chart"),
            ("scatter_plot", "Scatter Plot"),
            ("heatmap", "Heatmap"),
        ],
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Primary Chart Type",
        initial="stacked_bar",
        help_text="Primary visualization style for comparison results",
    )

    # Analysis options
    include_cost_breakdown = forms.BooleanField(
        label="Include Detailed Cost Breakdown",
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "filled-in"}),
        help_text="Show detailed breakdown of cost components for each configuration",
    )

    normalize_by_baseline = forms.BooleanField(
        label="Normalize to Baseline",
        initial=False,
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "filled-in"}),
        help_text="Express results as percentage relative to a baseline configuration",
    )

    baseline_configuration = forms.CharField(
        max_length=200,
        label="Baseline Configuration",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Auto-select first configuration"}
        ),
        required=False,
        help_text="Reference configuration for normalization (leave blank for auto-selection)",
    )

    sensitivity_analysis = forms.BooleanField(
        label="Include Sensitivity Analysis",
        initial=False,
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "filled-in"}),
        help_text="Perform sensitivity analysis on key parameters across configurations",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate dropdown choices from demo data similar to parameter form
        self._populate_grouping_choices()

    def _populate_grouping_choices(self):
        """Populate grouping choice options from available T3CO demo data"""
        try:
            # Get demo_inputs path
            main_project_root = settings.BASE_DIR.parent
            demo_path = os.path.join(main_project_root, "demo_inputs", "inputs")

            vehicle_file = os.path.join(demo_path, "Demo_FY22_vehicle_model_assumptions.csv")
            scenario_file = os.path.join(demo_path, "Demo_FY22_scenario_assumptions.csv")

            # This would be expanded to provide dynamic choices based on available data
            # For now, keeping static choices that match the data structure

        except Exception as e:
            print(f"Error populating grouping choices: {e}")

    def clean(self):
        cleaned_data = super().clean()
        selection_method = cleaned_data.get("selection_method")

        # Validate based on selection method
        if selection_method == "dropdown":
            if not cleaned_data.get("vehicle_configurations"):
                raise forms.ValidationError("Please select at least one vehicle configuration for comparison.")
        elif selection_method == "file_upload":
            if not cleaned_data.get("vehicle_files") and not cleaned_data.get("scenario_files"):
                raise forms.ValidationError("Please upload at least one vehicle or scenario file.")

        # Validate grouping combinations
        primary_group = cleaned_data.get("group_by_primary")
        secondary_group = cleaned_data.get("group_by_secondary")
        
        if primary_group == secondary_group and primary_group != "none":
            raise forms.ValidationError("Primary and secondary grouping cannot be the same.")

        return cleaned_data


class FleetAnalysisForm(forms.Form):
    """Form for fleet-level analysis."""

    fleet_name = forms.CharField(
        max_length=200,
        label="Fleet Name",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter fleet name"}
        ),
    )

    vehicle_files = MultipleFileField(
        label="Vehicle Files",
        validators=[FileExtensionValidator(allowed_extensions=["json", "csv"])],
        widget=MultipleFileInput(
            attrs={"class": "form-control", "accept": ".json,.csv"}
        ),
        help_text="Upload all vehicle files for fleet analysis",
    )

    scenario_files = MultipleFileField(
        label="Scenario Files",
        validators=[FileExtensionValidator(allowed_extensions=["json", "csv"])],
        widget=MultipleFileInput(
            attrs={"class": "form-control", "accept": ".json,.csv"}
        ),
        help_text="Upload scenario files for different use cases",
    )

    fleet_size = forms.IntegerField(
        min_value=1,
        max_value=10000,
        label="Fleet Size",
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Enter total fleet size"}
        ),
        help_text="Total number of vehicles in the fleet",
    )

    analysis_period = forms.ChoiceField(
        choices=[(5, "5 years"), (10, "10 years"), (15, "15 years"), (20, "20 years")],
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Analysis Period",
        initial=10,
        help_text="Analysis time horizon in years",
    )

    optimization_target = forms.ChoiceField(
        choices=[
            ("min_cost", "Minimize Total Cost"),
            ("min_emissions", "Minimize Emissions"),
            ("max_efficiency", "Maximize Efficiency"),
            ("balanced", "Balanced Approach"),
        ],
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Optimization Target",
        initial="min_cost",
        help_text="Primary optimization objective for fleet analysis",
    )


class VehicleUploadForm(forms.Form):
    """Form for uploading vehicle configuration files."""

    vehicle_name = forms.CharField(
        max_length=200,
        label="Vehicle Name",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter vehicle name"}
        ),
    )

    vehicle_file = forms.FileField(
        label="Vehicle Configuration File",
        validators=[FileExtensionValidator(allowed_extensions=["json", "csv"])],
        widget=forms.ClearableFileInput(
            attrs={"class": "form-control", "accept": ".json,.csv"}
        ),
    )

    vehicle_type = forms.ChoiceField(
        choices=[
            ("conventional", "Conventional ICE"),
            ("hybrid", "Hybrid Electric"),
            ("plugin_hybrid", "Plug-in Hybrid"),
            ("battery_electric", "Battery Electric"),
            ("fuel_cell", "Fuel Cell Electric"),
            ("other", "Other"),
        ],
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Vehicle Type",
    )

    description = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Vehicle description (optional)",
            }
        ),
        label="Description",
        required=False,
    )


class ScenarioUploadForm(forms.Form):
    """Form for uploading scenario configuration files."""

    scenario_name = forms.CharField(
        max_length=200,
        label="Scenario Name",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter scenario name"}
        ),
    )

    scenario_file = forms.FileField(
        label="Scenario Configuration File",
        validators=[FileExtensionValidator(allowed_extensions=["json", "csv"])],
        widget=forms.ClearableFileInput(
            attrs={"class": "form-control", "accept": ".json,.csv"}
        ),
    )

    scenario_type = forms.ChoiceField(
        choices=[
            ("urban", "Urban Delivery"),
            ("highway", "Highway Transport"),
            ("mixed", "Mixed Use"),
            ("long_haul", "Long Haul"),
            ("regional", "Regional"),
            ("custom", "Custom Scenario"),
        ],
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Scenario Type",
    )

    description = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Scenario description (optional)",
            }
        ),
        label="Description",
        required=False,
    )


class DemoAnalysisForm(forms.Form):
    """Form for running demo analysis with sample data."""

    demo_vehicle = forms.ChoiceField(
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Demo Vehicle",
        help_text="Select a demo vehicle configuration",
    )

    demo_scenario = forms.ChoiceField(
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Demo Scenario",
        help_text="Select a demo scenario",
    )

    def __init__(self, *args, **kwargs):
        demo_vehicles = kwargs.pop("demo_vehicles", [])
        demo_scenarios = kwargs.pop("demo_scenarios", [])
        super().__init__(*args, **kwargs)

        self.fields["demo_vehicle"].choices = [
            (vehicle, vehicle) for vehicle in demo_vehicles
        ]
        self.fields["demo_scenario"].choices = [
            (scenario, scenario) for scenario in demo_scenarios
        ]


# Legacy forms for backward compatibility
class VehicleForm(forms.Form):
    """Legacy vehicle form."""

    vehicle_file = forms.FileField(label="Upload Vehicle Input File", required=True)


class ScenarioForm(forms.Form):
    """Legacy scenario form."""

    scenario_file = forms.FileField(label="Upload Scenario Input File", required=True)
