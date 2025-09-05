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
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter analysis name'})
    )
    
    # Vehicle selection
    vehicle_type = forms.ChoiceField(
        label="Vehicle Type",
        choices=[],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Analysis year
    analysis_year = forms.ChoiceField(
        label="Analysis Year",
        choices=[],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Scenario/vocation
    vocation = forms.ChoiceField(
        label="Vocation",
        choices=[],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Region for fuel prices
    region = forms.ChoiceField(
        label="Region",
        choices=[],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Key adjustable parameters
    drag_coefficient = forms.FloatField(
        label="Drag Coefficient",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'})
    )
    
    frontal_area_m2 = forms.FloatField(
        label="Frontal Area (m²)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'})
    )
    
    glider_kg = forms.FloatField(
        label="Glider Weight (kg)",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    cargo_kg = forms.FloatField(
        label="Cargo Weight (kg)",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    min_range_miles = forms.FloatField(
        label="Minimum Range (miles)",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    # Economic parameters
    discount_rate_pct = forms.FloatField(
        label="Discount Rate (%)",
        initial=4.1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'})
    )
    
    vehicle_life_yr = forms.IntegerField(
        label="Vehicle Life (years)",
        initial=7,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    annual_vmt = forms.FloatField(
        label="Annual VMT",
        initial=100000,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._populate_choices()
        self._set_initial_values()
    
    def _populate_choices(self):
        """Populate form choices from demo data"""
        try:
            # Get demo_inputs path - should be relative to the main project root
            # BASE_DIR is t3co_go_django directory, so we need to go up two levels to reach the main project
            main_project_root = settings.BASE_DIR.parent.parent
            demo_inputs_path = os.path.join(main_project_root, 'demo_inputs')
            
            # Vehicle types from vehicles directory
            vehicles_path = os.path.join(demo_inputs_path, 'vehicles')
            if os.path.exists(vehicles_path):
                vehicle_types = [(d, d.replace('_', ' ').title()) 
                               for d in os.listdir(vehicles_path) 
                               if os.path.isdir(os.path.join(vehicles_path, d)) and not d.startswith('.')]
                self.fields['vehicle_type'].choices = vehicle_types
            
            # Years from baseline vehicle data
            baseline_path = os.path.join(demo_inputs_path, 'auxiliary', 'BaselineVehicle.csv')
            if os.path.exists(baseline_path):
                df = pd.read_csv(baseline_path)
                years = [(str(year), str(year)) for year in sorted(df['Year'].unique())]
                self.fields['analysis_year'].choices = years
            
            # Vocations from vocation requirements
            vocation_path = os.path.join(demo_inputs_path, 'auxiliary', 'VocationRequirements.csv')
            if os.path.exists(vocation_path):
                df = pd.read_csv(vocation_path)
                vocations = [(v, v.title()) for v in sorted(df['vocation'].unique())]
                self.fields['vocation'].choices = vocations
            
            # Regions from fuel prices
            fuel_path = os.path.join(demo_inputs_path, 'auxiliary', 'FuelPrices.csv')
            if os.path.exists(fuel_path):
                df = pd.read_csv(fuel_path)
                regions = [(r, r) for r in sorted(df['Region'].unique())]
                self.fields['region'].choices = regions
                
        except Exception as e:
            print(f"Error populating form choices: {e}")
            # Set default choices if data loading fails
            self.fields['vehicle_type'].choices = [('Class8_long_haul', 'Class 8 Long Haul')]
            self.fields['analysis_year'].choices = [('2025', '2025')]
            self.fields['vocation'].choices = [('Long haul', 'Long Haul')]
            self.fields['region'].choices = [('Pacific', 'Pacific')]
    
    def _set_initial_values(self):
        """Set initial values for parameters based on demo data"""
        try:
            # Get demo_inputs path - should be relative to the main project root
            main_project_root = settings.BASE_DIR.parent.parent
            demo_inputs_path = os.path.join(main_project_root, 'demo_inputs')
            baseline_path = os.path.join(demo_inputs_path, 'auxiliary', 'BaselineVehicle.csv')
            
            if os.path.exists(baseline_path):
                df = pd.read_csv(baseline_path)
                # Use 2025 data as default
                default_row = df[df['Year'] == 2025].iloc[0] if not df[df['Year'] == 2025].empty else df.iloc[0]
                
                self.fields['drag_coefficient'].initial = default_row.get('dragCoef', 0.546)
                self.fields['frontal_area_m2'].initial = default_row.get('frontalAreaM2', 10.18)
                self.fields['glider_kg'].initial = default_row.get('gliderKg', 11776)
            
            # Set cargo from vocation requirements
            vocation_path = os.path.join(demo_inputs_path, 'auxiliary', 'VocationRequirements.csv')
            if os.path.exists(vocation_path):
                df = pd.read_csv(vocation_path)
                default_row = df[df['Year'] == 2025].iloc[0] if not df[df['Year'] == 2025].empty else df.iloc[0]
                
                self.fields['cargo_kg'].initial = default_row.get('cargoKg', 16329)
                self.fields['min_range_miles'].initial = 750  # Default range
                
        except Exception as e:
            print(f"Error setting initial values: {e}")
            # Set fallback defaults
            self.fields['drag_coefficient'].initial = 0.546
            self.fields['frontal_area_m2'].initial = 10.18
            self.fields['glider_kg'].initial = 11776
            self.fields['cargo_kg'].initial = 16329
            self.fields['min_range_miles'].initial = 750


class VehicleComparisonForm(forms.Form):
    """Form for comparing multiple vehicles."""

    comparison_name = forms.CharField(
        max_length=200,
        label="Comparison Name",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter comparison name"}
        ),
    )

    vehicle_files = MultipleFileField(
        label="Vehicle Files",
        validators=[FileExtensionValidator(allowed_extensions=["json", "csv"])],
        widget=MultipleFileInput(
            attrs={"class": "form-control", "accept": ".json,.csv"}
        ),
        help_text="Upload multiple vehicle files to compare (JSON or CSV format)",
    )

    scenario_file = forms.FileField(
        label="Scenario File",
        validators=[FileExtensionValidator(allowed_extensions=["json", "csv"])],
        widget=forms.ClearableFileInput(
            attrs={"class": "form-control", "accept": ".json,.csv"}
        ),
        help_text="Upload scenario file for comparison analysis",
    )

    comparison_metrics = forms.MultipleChoiceField(
        choices=[
            ("total_cost", "Total Cost of Ownership"),
            ("cost_per_mile", "Cost per Mile"),
            ("fuel_cost", "Fuel Costs"),
            ("maintenance_cost", "Maintenance Costs"),
            ("depreciation", "Depreciation"),
            ("operating_cost", "Operating Costs"),
        ],
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
        label="Comparison Metrics",
        required=False,
        help_text="Select metrics to compare (default: all metrics)",
    )


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
