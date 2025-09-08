from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.conf import settings
from datetime import datetime
import os
import json

from .forms import (
    TCOAnalysisForm,
    VehicleComparisonForm,
    FleetAnalysisForm,
    TCOAnalysisParameterForm,
)
from .models import Analysis, Vehicle, Scenario
from core.t3co_integration import T3COIntegration


def dashboard(request):
    """Main dashboard view with recent analyses and quick stats."""
    recent_analyses = Analysis.objects.order_by("-created_at")[:5]
    total_analyses = Analysis.objects.count()
    total_vehicles = Vehicle.objects.count()
    total_scenarios = Scenario.objects.count()

    context = {
        "recent_analyses": recent_analyses,
        "total_analyses": total_analyses,
        "total_vehicles": total_vehicles,
        "total_scenarios": total_scenarios,
    }
    return render(request, "t3co_app/dashboard.html", context)


def vehicle_list(request):
    """Display list of all vehicles."""
    vehicles = Vehicle.objects.all()
    return render(request, "t3co_app/vehicle_list.html", {"vehicles": vehicles})


def scenario_list(request):
    """Display list of all scenarios."""
    scenarios = Scenario.objects.all()
    return render(request, "t3co_app/scenario_list.html", {"scenarios": scenarios})


def tco_analysis(request):
    """Single vehicle TCO analysis with Chart.js visualizations."""
    if request.method == "POST":
        form = TCOAnalysisForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Initialize T3CO integration
                t3co = T3COIntegration()

                # Get form data
                vehicle_file = form.cleaned_data["vehicle_file"]
                scenario_file = form.cleaned_data["scenario_file"]
                analysis_name = form.cleaned_data["analysis_name"]

                # Save uploaded files temporarily
                vehicle_path = default_storage.save(
                    f"temp/{vehicle_file.name}", vehicle_file
                )
                scenario_path = default_storage.save(
                    f"temp/{scenario_file.name}", scenario_file
                )

                # Convert relative paths to absolute
                vehicle_abs_path = os.path.join(settings.MEDIA_ROOT, vehicle_path)
                scenario_abs_path = os.path.join(settings.MEDIA_ROOT, scenario_path)

                # Run T3CO analysis
                results = t3co.perform_tco_analysis(
                    vehicle_files=[vehicle_abs_path], scenario_files=[scenario_abs_path]
                )

                if results and results.get("success"):
                    # Prepare Chart.js data
                    chart_data = prepare_single_analysis_charts(results)

                    # Save analysis to database
                    analysis = Analysis.objects.create(
                        name=analysis_name,
                        analysis_type="single",
                        vehicle_file=vehicle_file.name,
                        scenario_file=scenario_file.name,
                        results=results,
                    )

                    # Clean up temporary files
                    default_storage.delete(vehicle_path)
                    default_storage.delete(scenario_path)

                    context = {
                        "analysis": analysis,
                        "results": results,
                        "chart_data": chart_data,
                        "form": TCOAnalysisForm(),
                    }
                    return render(request, "t3co_app/analysis_results.html", context)
                else:
                    error_msg = results.get(
                        "error", "Unknown error occurred during analysis"
                    )
                    messages.error(request, f"Analysis failed: {error_msg}")

            except Exception as e:
                messages.error(request, f"Error during analysis: {str(e)}")
                # Clean up files on error
                try:
                    default_storage.delete(vehicle_path)
                    default_storage.delete(scenario_path)
                except Exception:
                    pass
    else:
        form = TCOAnalysisForm()

    return render(request, "t3co_app/tco_analysis.html", {"form": form})


def tco_parameter_analysis(request):
    """Parameter-based TCO analysis using dropdowns and form inputs."""
    if request.method == "POST":
        form = TCOAnalysisParameterForm(request.POST)
        if form.is_valid():
            try:
                # Initialize T3CO integration
                t3co = T3COIntegration()

                # Get form data
                form_data = form.cleaned_data
                analysis_name = form_data.get("analysis_name", "Parameter Analysis")

                # Run parameter-based analysis
                results = t3co.perform_parameter_based_analysis(form_data)

                if results and results.get("success"):
                    # Prepare Chart.js data
                    chart_data = prepare_parameter_analysis_charts(results)

                    # Save analysis to database
                    analysis = Analysis.objects.create(
                        name=analysis_name,
                        analysis_type="parameter",
                        results=results,
                    )

                    # Redirect to the dedicated results page with enhanced visualizations
                    return redirect(
                        "parameter_analysis_results", analysis_id=analysis.id
                    )
                else:
                    error_msg = results.get(
                        "error", "Unknown error occurred during parameter analysis"
                    )
                    messages.error(request, f"Analysis failed: {error_msg}")

            except Exception as e:
                messages.error(request, f"Error during parameter analysis: {str(e)}")
    else:
        form = TCOAnalysisParameterForm()

    return render(request, "t3co_app/tco_parameter_analysis.html", {"form": form})


def parameter_analysis_results(request, analysis_id):
    """Display parameter analysis results with enhanced Chart.js visualizations."""
    try:
        analysis = Analysis.objects.get(id=analysis_id)

        # Debug: Print the actual results structure
        print(f"=== Analysis ID {analysis_id} - {analysis.name} ===")
        print(f"Results type: {type(analysis.results)}")
        if analysis.results:
            print(f"Results keys: {list(analysis.results.keys())}")

            # Look for discounted_tco and other key fields
            for key, value in analysis.results.items():
                if isinstance(value, dict):
                    print(
                        f"  {key}: dict with {len(value)} keys - {list(value.keys())[:5]}..."
                    )
                elif isinstance(value, list):
                    print(f"  {key}: list with {len(value)} items")
                else:
                    print(f"  {key}: {type(value).__name__} = {value}")
        print("=== End Debug ===")

        # Prepare enhanced Chart.js data from stored results using Ledger format
        chart_data = prepare_ledger_analysis_charts(analysis.results)

        # JSON serialize chart data for template
        import json

        chart_data_json = json.dumps(chart_data) if chart_data else "{}"

        context = {
            "analysis": analysis,
            "results": analysis.results,
            "chart_data": chart_data,
            "chart_data_json": chart_data_json,
            "chart_types_enabled": {
                "tco_breakdown": True,
                "cost_distribution": True,
                "key_metrics": True,
                "timeline": True,
                "radar": True,
            },
        }
        return render(request, "t3co_app/parameter_analysis_results.html", context)

    except Analysis.DoesNotExist:
        messages.error(request, f"Analysis with ID {analysis_id} not found.")
        return redirect("tco_parameter_analysis")
    except Exception as e:
        messages.error(request, f"Error loading analysis results: {str(e)}")
        return redirect("tco_parameter_analysis")


def demo_parameter_results(request):
    """Demo view to showcase parameter analysis results with enhanced Chart.js visualizations."""
    # Create demo analysis results that showcase our T3CO cost breakdown
    demo_results = {
        "success": True,
        "total_cost_of_ownership": 195000,
        "cost_per_mile": 0.975,
        "annual_cost": 28500,
        "vehicle_life_years": 7,
        "tco_breakdown": {
            "residual_cost_dol": -15000,  # Negative for residual value
            "glider_cost_dol": 25000,
            "fuel_converter_cost_dol": 35000,
            "fuel_storage_cost_dol": 8000,
            "motor_control_power_elecs_cost_dol": 15000,
            "plug_cost_dol": 500,
            "battery_cost_dol": 45000,
            "purchase_tax_dol": 3500,
            "insurance_cost_dol": 18000,
            "total_maintenance_cost_dol": 22000,
            "total_fuel_cost_dol": 32000,
            "fueling_dwell_labor_cost_dol": 4000,
            "discounted_downtime_oppy_cost_dol": 3500,
            "payload_capacity_cost_dol": 2000,
        },
        "kpis": {
            "fuel_efficiency_mpgge": 12.5,
            "range_miles": 650,
            "payload_impact": 0.95,
            "downtime_hours": 48,
        },
        "purchase_cost": 133000,
        "fuel_cost": 32000,
        "maintenance_cost": 22000,
        "insurance_cost": 18000,
        "t3co_version": "2.0 Enhanced",
    }

    # Create a demo analysis record
    analysis = Analysis.objects.create(
        name="Demo Parameter Analysis - Enhanced T3CO Charts",
        analysis_type="parameter",
        results=demo_results,
    )

    # Prepare enhanced Chart.js data
    chart_data = prepare_parameter_analysis_charts(demo_results)

    # Create form data for display
    demo_form_data = {
        "vehicle_type": "Class 8 Electric Truck",
        "analysis_year": "2030",
        "vocation": "Long Haul",
        "region": "FY22TechSuccess",
        "vehicle_life_yr": 7,
        "annual_vmt": 100000,
        "drag_coefficient": 0.546,
    }

    context = {
        "analysis": analysis,
        "results": demo_results,
        "chart_data": chart_data,
        "form_data": demo_form_data,
        "chart_types_enabled": {
            "tco_breakdown": True,
            "cost_distribution": True,
            "key_metrics": True,
            "timeline": True,
            "radar": True,
        },
    }

    return render(request, "t3co_app/parameter_analysis_results.html", context)


def debug_charts(request):
    """Debug page for testing chart functionality."""
    try:
        # Create simple test data
        demo_results = {
            "total_cost_of_ownership": 150000,
            "cost_per_mile": 0.60,
            "annual_cost": 22000,
            "tco_breakdown": {
                "glider_cost_dol": 40000,
                "fuel_converter_cost_dol": 20000,
                "battery_cost_dol": 30000,
                "total_fuel_cost_dol": 35000,
                "total_maintenance_cost_dol": 18000,
                "insurance_cost_dol": 7000,
            },
            "kpis": {"fuel_efficiency_mpgge": 8.2, "range_miles": 600},
        }

        # Generate chart data
        chart_data = prepare_parameter_analysis_charts(demo_results)

        context = {"chart_data": json.dumps(chart_data)}

        return render(request, "t3co_app/debug_charts.html", context)

    except Exception as e:
        print(f"Error in debug_charts: {e}")
        import traceback

        traceback.print_exc()

        context = {"chart_data": "{}", "error": str(e)}
        return render(request, "t3co_app/debug_charts.html", context)


def vehicle_comparison(request):
    """Enhanced multi-vehicle comparison analysis with grouping and Chart.js visualizations."""
    if request.method == "POST":
        form = VehicleComparisonForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                t3co = T3COIntegration()

                # Get form data
                comparison_name = form.cleaned_data["comparison_name"]
                selection_method = form.cleaned_data["selection_method"]

                vehicle_files = []
                scenario_files = []

                if selection_method == "file_upload":
                    # Handle file uploads
                    vehicle_files = request.FILES.getlist("vehicle_files")
                    scenario_files = request.FILES.getlist("scenario_files") or []

                    # Save files temporarily
                    vehicle_paths = []
                    scenario_paths = []

                    for vehicle_file in vehicle_files:
                        path = default_storage.save(
                            f"temp/{vehicle_file.name}", vehicle_file
                        )
                        vehicle_paths.append(os.path.join(settings.MEDIA_ROOT, path))

                    for scenario_file in scenario_files:
                        path = default_storage.save(
                            f"temp/{scenario_file.name}", scenario_file
                        )
                        scenario_paths.append(os.path.join(settings.MEDIA_ROOT, path))

                    # Run comparison analysis
                    results = t3co.perform_tco_analysis(
                        vehicle_files=vehicle_paths,
                        scenario_files=scenario_paths if scenario_paths else None,
                    )

                elif selection_method == "dropdown":
                    # Handle dropdown-based selections
                    vehicle_configurations = form.cleaned_data.get(
                        "vehicle_configurations"
                    )
                    if vehicle_configurations:
                        import json

                        configs = json.loads(vehicle_configurations)

                        # Generate vehicle-scenario combinations from dropdown selections
                        results = t3co.perform_parameter_based_comparison(configs)
                    else:
                        raise ValueError("No vehicle configurations provided")
                else:
                    raise ValueError(f"Invalid selection method: {selection_method}")

                if results and results.get("success"):
                    # Prepare Chart.js comparison data with grouping
                    form_data = form.cleaned_data
                    chart_data = prepare_comparison_charts(
                        results, vehicle_files, form_data
                    )

                    # Save comparison analysis
                    analysis = Analysis.objects.create(
                        name=comparison_name,
                        analysis_type="comparison",
                        results=results,
                    )

                    # Clean up temporary files if used
                    if selection_method == "file_upload":
                        for path in vehicle_paths:
                            rel_path = os.path.relpath(path, settings.MEDIA_ROOT)
                            default_storage.delete(rel_path)
                        for path in scenario_paths:
                            rel_path = os.path.relpath(path, settings.MEDIA_ROOT)
                            default_storage.delete(rel_path)

                    context = {
                        "analysis": analysis,
                        "results": results,
                        "chart_data": chart_data,
                        "form_data": form_data,
                        "vehicle_names": [f.name for f in vehicle_files]
                        if vehicle_files
                        else [],
                        "scenario_names": [f.name for f in scenario_files]
                        if scenario_files
                        else [],
                        "form": VehicleComparisonForm(),
                    }
                    return render(request, "t3co_app/comparison_results.html", context)
                else:
                    error_msg = results.get(
                        "error", "Unknown error occurred during comparison"
                    )
                    messages.error(request, f"Comparison failed: {error_msg}")

            except Exception as e:
                messages.error(request, f"Error during comparison: {str(e)}")
                # Clean up files on error
                try:
                    if "vehicle_paths" in locals():
                        for path in vehicle_paths:
                            rel_path = os.path.relpath(path, settings.MEDIA_ROOT)
                            default_storage.delete(rel_path)
                    if "scenario_paths" in locals():
                        for path in scenario_paths:
                            rel_path = os.path.relpath(path, settings.MEDIA_ROOT)
                            default_storage.delete(rel_path)
                except Exception:
                    pass
    else:
        form = VehicleComparisonForm()

    return render(request, "t3co_app/vehicle_comparison.html", {"form": form})


def fleet_analysis(request):
    """Fleet-level analysis with multiple vehicles and scenarios."""
    if request.method == "POST":
        form = FleetAnalysisForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                t3co = T3COIntegration()

                # Get form data
                vehicle_files = request.FILES.getlist("vehicle_files")
                scenario_files = request.FILES.getlist("scenario_files")
                fleet_name = form.cleaned_data["fleet_name"]

                # Save files temporarily
                vehicle_paths = []
                scenario_paths = []

                for vehicle_file in vehicle_files:
                    path = default_storage.save(
                        f"temp/{vehicle_file.name}", vehicle_file
                    )
                    vehicle_paths.append(os.path.join(settings.MEDIA_ROOT, path))

                for scenario_file in scenario_files:
                    path = default_storage.save(
                        f"temp/{scenario_file.name}", scenario_file
                    )
                    scenario_paths.append(os.path.join(settings.MEDIA_ROOT, path))

                # Run fleet analysis
                results = t3co.perform_tco_analysis(
                    vehicle_files=vehicle_paths, scenario_files=scenario_paths
                )

                if results and results.get("success"):
                    # Prepare Chart.js fleet data
                    chart_data = prepare_fleet_charts(
                        results, vehicle_files, scenario_files
                    )

                    # Save fleet analysis
                    analysis = Analysis.objects.create(
                        name=fleet_name, analysis_type="fleet", results=results
                    )

                    # Clean up temporary files
                    for path in vehicle_paths:
                        rel_path = os.path.relpath(path, settings.MEDIA_ROOT)
                        default_storage.delete(rel_path)
                    for path in scenario_paths:
                        rel_path = os.path.relpath(path, settings.MEDIA_ROOT)
                        default_storage.delete(rel_path)

                    context = {
                        "analysis": analysis,
                        "results": results,
                        "chart_data": chart_data,
                        "vehicle_names": [f.name for f in vehicle_files],
                        "scenario_names": [f.name for f in scenario_files],
                        "form": FleetAnalysisForm(),
                    }
                    return render(request, "t3co_app/fleet_results.html", context)
                else:
                    error_msg = results.get(
                        "error", "Unknown error occurred during fleet analysis"
                    )
                    messages.error(request, f"Fleet analysis failed: {error_msg}")

            except Exception as e:
                messages.error(request, f"Error during fleet analysis: {str(e)}")
                # Clean up files on error
                try:
                    for path in vehicle_paths:
                        rel_path = os.path.relpath(path, settings.MEDIA_ROOT)
                        default_storage.delete(rel_path)
                    for path in scenario_paths:
                        rel_path = os.path.relpath(path, settings.MEDIA_ROOT)
                        default_storage.delete(rel_path)
                except Exception:
                    pass
    else:
        form = FleetAnalysisForm()

    return render(request, "t3co_app/fleet_analysis.html", {"form": form})


def analysis_detail(request, analysis_id):
    """View detailed results of a specific analysis."""
    try:
        analysis = Analysis.objects.get(id=analysis_id)

        # Prepare chart data based on analysis type
        if analysis.analysis_type == "single":
            chart_data = prepare_single_analysis_charts(analysis.results)
        elif analysis.analysis_type == "comparison":
            chart_data = prepare_comparison_charts(analysis.results, [])
        elif analysis.analysis_type == "fleet":
            chart_data = prepare_fleet_charts(analysis.results, [], [])
        else:
            chart_data = {}

        context = {
            "analysis": analysis,
            "chart_data": chart_data,
        }
        return render(request, "t3co_app/analysis_detail.html", context)
    except Analysis.DoesNotExist:
        messages.error(request, "Analysis not found.")
        return redirect("dashboard")


@require_http_methods(["GET"])
def demo_data(request):
    """Load demo data for quick testing."""
    try:
        t3co = T3COIntegration()
        demo_vehicles, demo_scenarios = t3co.get_demo_data()

        context = {
            "demo_vehicles": demo_vehicles,
            "demo_scenarios": demo_scenarios,
        }
        return render(request, "t3co_app/demo_data.html", context)
    except Exception as e:
        messages.error(request, f"Error loading demo data: {str(e)}")
        return redirect("dashboard")


@require_http_methods(["POST"])
def get_vehicle_parameters(request):
    """AJAX endpoint to get vehicle parameters based on dropdown selections."""
    try:
        import json

        # Parse JSON body
        body_data = json.loads(request.body.decode("utf-8"))

        # Initialize T3CO integration
        t3co = T3COIntegration()

        # Get vehicle parameters based on selections
        parameters = t3co.get_vehicle_parameters_by_selection(body_data)

        if parameters:
            return JsonResponse({"success": True, "parameters": parameters})
        else:
            return JsonResponse(
                {
                    "success": False,
                    "error": "No parameters found for the selected vehicle configuration",
                }
            )

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})
    """Run a quick demo analysis with sample data."""
    try:
        t3co = T3COIntegration()
        demo_vehicles, demo_scenarios = t3co.get_demo_data()

        if not demo_vehicles or not demo_scenarios:
            return JsonResponse({"success": False, "error": "No demo data available"})

        # Use first available demo files
        results = t3co.perform_tco_analysis(
            vehicle_files=[demo_vehicles[0]], scenario_files=[demo_scenarios[0]]
        )

        if results and results.get("success"):
            chart_data = prepare_single_analysis_charts(results)

            # Save demo analysis
            analysis = Analysis.objects.create(
                name="Demo Analysis",
                analysis_type="demo",
                vehicle_file=os.path.basename(demo_vehicles[0]),
                scenario_file=os.path.basename(demo_scenarios[0]),
                results=results,
            )

            return JsonResponse(
                {
                    "success": True,
                    "analysis_id": analysis.id,
                    "results": results,
                    "chart_data": chart_data,
                }
            )
        else:
            return JsonResponse(
                {
                    "success": False,
                    "error": results.get("error", "Demo analysis failed"),
                }
            )

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@require_http_methods(["POST"])
def run_demo_analysis(request):
    """Run a quick demo analysis with sample data."""
    try:
        t3co = T3COIntegration()
        demo_vehicles, demo_scenarios = t3co.get_demo_data()

        if not demo_vehicles or not demo_scenarios:
            return JsonResponse({"success": False, "error": "No demo data available"})

        # Use first available demo files
        results = t3co.perform_tco_analysis(
            vehicle_files=[demo_vehicles[0]], scenario_files=[demo_scenarios[0]]
        )

        if results and results.get("success"):
            chart_data = prepare_single_analysis_charts(results)

            # Save demo analysis
            analysis = Analysis.objects.create(
                name="Demo Analysis",
                analysis_type="demo",
                vehicle_file=os.path.basename(demo_vehicles[0]),
                scenario_file=os.path.basename(demo_scenarios[0]),
                results=results,
            )

            return JsonResponse(
                {
                    "success": True,
                    "analysis_id": analysis.id,
                    "results": results,
                    "chart_data": chart_data,
                }
            )
        else:
            return JsonResponse(
                {
                    "success": False,
                    "error": results.get("error", "Demo analysis failed"),
                }
            )

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


# Legacy view for backward compatibility
def analysis(request):
    """Legacy analysis view - redirects to tco_analysis."""
    return redirect("tco_analysis")


def results(request):
    """Legacy results view - redirects to dashboard."""
    return redirect("dashboard")


def prepare_single_analysis_charts(results):
    """Prepare Chart.js data for single vehicle analysis."""
    chart_data = {}

    try:
        # TCO Breakdown Pie Chart
        if "tco_breakdown" in results:
            breakdown = results["tco_breakdown"]
            chart_data["tco_breakdown"] = {
                "type": "pie",
                "data": {
                    "labels": list(breakdown.keys()),
                    "datasets": [
                        {
                            "data": list(breakdown.values()),
                            "backgroundColor": [
                                "#FF6384",
                                "#36A2EB",
                                "#FFCE56",
                                "#4BC0C0",
                                "#9966FF",
                                "#FF9F40",
                                "#FF6384",
                                "#C9CBCF",
                            ],
                        }
                    ],
                },
                "options": {
                    "responsive": True,
                    "plugins": {
                        "title": {
                            "display": True,
                            "text": "Total Cost of Ownership Breakdown",
                        },
                        "legend": {"position": "bottom"},
                    },
                },
            }

        # Annual Costs Bar Chart
        if "annual_costs" in results:
            annual = results["annual_costs"]
            chart_data["annual_costs"] = {
                "type": "bar",
                "data": {
                    "labels": list(annual.keys()),
                    "datasets": [
                        {
                            "label": "Annual Cost ($)",
                            "data": list(annual.values()),
                            "backgroundColor": "#36A2EB",
                            "borderColor": "#36A2EB",
                            "borderWidth": 1,
                        }
                    ],
                },
                "options": {
                    "responsive": True,
                    "plugins": {
                        "title": {"display": True, "text": "Annual Cost Components"}
                    },
                    "scales": {
                        "y": {
                            "beginAtZero": True,
                            "title": {"display": True, "text": "Cost ($)"},
                        }
                    },
                },
            }

        # Cost per Mile Line Chart
        if "cost_per_mile_timeline" in results:
            timeline = results["cost_per_mile_timeline"]
            chart_data["cost_per_mile"] = {
                "type": "line",
                "data": {
                    "labels": list(timeline.keys()),
                    "datasets": [
                        {
                            "label": "Cost per Mile ($/mile)",
                            "data": list(timeline.values()),
                            "borderColor": "#FF6384",
                            "backgroundColor": "rgba(255, 99, 132, 0.1)",
                            "tension": 0.4,
                        }
                    ],
                },
                "options": {
                    "responsive": True,
                    "plugins": {
                        "title": {"display": True, "text": "Cost per Mile Over Time"}
                    },
                    "scales": {
                        "y": {
                            "beginAtZero": True,
                            "title": {
                                "display": True,
                                "text": "Cost per Mile ($/mile)",
                            },
                        },
                        "x": {"title": {"display": True, "text": "Year"}},
                    },
                },
            }

    except Exception as e:
        print(f"Error preparing single analysis charts: {e}")

    return chart_data


def prepare_comparison_charts(results, vehicle_files=None, comparison_form_data=None):
    """Prepare Chart.js data for vehicle comparison with enhanced grouping capabilities."""
    chart_data = {}

    try:
        # Extract form data for grouping preferences
        group_by_primary = (
            comparison_form_data.get("group_by_primary", "fuel_type")
            if comparison_form_data
            else "fuel_type"
        )
        group_by_secondary = (
            comparison_form_data.get("group_by_secondary", "none")
            if comparison_form_data
            else "none"
        )
        chart_type = (
            comparison_form_data.get("chart_type", "stacked_bar")
            if comparison_form_data
            else "stacked_bar"
        )
        comparison_metrics = (
            comparison_form_data.get("comparison_metrics", ["total_cost"])
            if comparison_form_data
            else ["total_cost"]
        )
        include_breakdown = (
            comparison_form_data.get("include_cost_breakdown", True)
            if comparison_form_data
            else True
        )

        # Define T3CO cost categories with colors (matching old charts.py)
        cost_categories = {
            "residual_cost_dol": {"label": "Residual Cost", "color": "#6C7B8B"},
            "glider_cost_dol": {"label": "Glider Cost", "color": "#8b7355"},
            "fuel_converter_cost_dol": {
                "label": "Fuel Converter Cost",
                "color": "#228B22",
            },
            "fuel_storage_cost_dol": {"label": "Fuel Storage Cost", "color": "#8B4513"},
            "motor_control_power_elecs_cost_dol": {
                "label": "Motor/Power Electronics",
                "color": "#1874CD",
            },
            "plug_cost_dol": {"label": "Plug Cost", "color": "#6A5ACD"},
            "battery_cost_dol": {"label": "Battery Cost", "color": "#7EC0EE"},
            "purchase_tax_dol": {"label": "Purchase Tax", "color": "#CD5B45"},
            "insurance_cost_dol": {"label": "Insurance Cost", "color": "#CDC673"},
            "total_maintenance_cost_dol": {
                "label": "Maintenance Cost",
                "color": "#DAA520",
            },
            "total_fuel_cost_dol": {"label": "Fuel Cost", "color": "#4682B4"},
            "fueling_dwell_labor_cost_dol": {
                "label": "Fueling/Dwell Labor",
                "color": "#CD2626",
            },
            "discounted_downtime_oppy_cost_dol": {
                "label": "Downtime Opportunity Cost",
                "color": "#8B0000",
            },
            "payload_capacity_cost_dol": {
                "label": "Payload Capacity Cost",
                "color": "#CD8C95",
            },
        }

        # Parse comparison results data
        comparison_data = results.get("comparison_results", [])
        if not comparison_data:
            # Fallback for legacy format
            comparison_data = results.get("scenarios", [])

        if not comparison_data:
            print("No comparison data found in results")
            return chart_data

        # Group data by primary and secondary groupings
        grouped_data = {}
        labels = []

        for idx, scenario_result in enumerate(comparison_data):
            # Extract grouping values from scenario data
            scenario_name = scenario_result.get("scenario_name", f"Scenario {idx + 1}")
            labels.append(scenario_name)

            # Parse scenario name to extract grouping components
            parsed_components = parse_scenario_components(scenario_name)

            primary_group_value = parsed_components.get(group_by_primary, "Unknown")
            secondary_group_value = (
                parsed_components.get(group_by_secondary, "None")
                if group_by_secondary != "none"
                else "None"
            )

            group_key = f"{primary_group_value}"
            if group_by_secondary != "none":
                group_key = f"{primary_group_value} - {secondary_group_value}"

            if group_key not in grouped_data:
                grouped_data[group_key] = []

            grouped_data[group_key].append(
                {"label": scenario_name, "data": scenario_result, "index": idx}
            )

        # Generate Primary Comparison Chart - Stacked TCO Breakdown
        if include_breakdown and chart_type == "stacked_bar":
            chart_data["tco_stacked_comparison"] = create_stacked_comparison_chart(
                grouped_data,
                cost_categories,
                labels,
                group_by_primary,
                group_by_secondary,
            )

        # Generate Metrics Comparison Charts
        for metric in comparison_metrics:
            if metric == "total_cost":
                chart_data["total_cost_comparison"] = create_metric_comparison_chart(
                    grouped_data,
                    "discounted_tco_dol",
                    "Total Cost of Ownership",
                    group_by_primary,
                    chart_type,
                )
            elif metric == "cost_per_mile":
                chart_data["cost_per_mile_comparison"] = create_metric_comparison_chart(
                    grouped_data,
                    "cost_per_mile",
                    "Cost per Mile",
                    group_by_primary,
                    chart_type,
                )
            elif metric == "fuel_efficiency":
                chart_data["fuel_efficiency_comparison"] = (
                    create_metric_comparison_chart(
                        grouped_data,
                        "fuel_efficiency_mpgge",
                        "Fuel Efficiency (MPGGE)",
                        group_by_primary,
                        chart_type,
                    )
                )

        # Generate Grouped Matrix Chart if secondary grouping is specified
        if group_by_secondary != "none":
            chart_data["matrix_comparison"] = create_matrix_comparison_chart(
                grouped_data, group_by_primary, group_by_secondary, comparison_metrics
            )

        # Generate Summary Statistics Chart
        chart_data["comparison_summary"] = create_comparison_summary_chart(
            grouped_data, comparison_metrics
        )

    except Exception as e:
        print(f"Error preparing comparison charts: {e}")

    return chart_data


def parse_scenario_components(scenario_name):
    """Parse scenario name into components for grouping"""
    import re

    components = {
        "vehicle_class": "Unknown",
        "fuel_type": "Unknown",
        "analysis_year": "Unknown",
        "program_status": "Unknown",
        "vocation": "Unknown",
        "region": "Unknown",
    }

    try:
        # Extract vehicle class (Class 8, Class 6, etc.)
        class_match = re.search(r"Class\s+(\d+)", scenario_name)
        if class_match:
            components["vehicle_class"] = f"Class {class_match.group(1)}"

        # Extract content in parentheses: (fuel_type, year, program_status)
        paren_match = re.search(r"\(([^)]+)\)", scenario_name)
        if paren_match:
            paren_content = paren_match.group(1)
            parts = [part.strip() for part in paren_content.split(",")]

            if len(parts) >= 3:
                components["fuel_type"] = parts[0]
                components["analysis_year"] = parts[1]
                components["program_status"] = parts[2]
            elif len(parts) >= 2:
                components["fuel_type"] = parts[0]
                components["analysis_year"] = parts[1]
            elif len(parts) >= 1:
                if parts[0].isdigit():
                    components["analysis_year"] = parts[0]
                else:
                    components["fuel_type"] = parts[0]

    except Exception as e:
        print(f"Error parsing scenario name '{scenario_name}': {e}")

    return components


def create_stacked_comparison_chart(
    grouped_data, cost_categories, labels, primary_group, secondary_group
):
    """Create a stacked bar chart for TCO cost breakdown comparison"""

    # Prepare datasets for stacking
    datasets = []
    cost_keys = list(cost_categories.keys())

    # Get all scenario data
    all_scenarios = []
    group_labels = []

    for group_name, scenarios in grouped_data.items():
        group_labels.append(group_name)
        for scenario in scenarios:
            all_scenarios.append(scenario)

    # Create dataset for each cost component
    for cost_key in cost_keys:
        if cost_key in cost_categories:
            category = cost_categories[cost_key]
            cost_data = []

            for scenario in all_scenarios:
                cost_value = scenario["data"].get(cost_key, 0)
                cost_data.append(cost_value)

            # Only add if there's meaningful data
            if any(val > 0 for val in cost_data):
                datasets.append(
                    {
                        "label": category["label"],
                        "data": cost_data,
                        "backgroundColor": category["color"],
                        "borderColor": category["color"],
                        "borderWidth": 1,
                    }
                )

    scenario_labels = [scenario["label"] for scenario in all_scenarios]

    return {
        "type": "bar",
        "data": {"labels": scenario_labels, "datasets": datasets},
        "options": {
            "responsive": True,
            "plugins": {
                "title": {
                    "display": True,
                    "text": f"TCO Cost Breakdown Comparison (Grouped by {primary_group.replace('_', ' ').title()})",
                },
                "legend": {"position": "bottom", "labels": {"usePointStyle": True}},
                "tooltip": {
                    "callbacks": {
                        "label": "function(context) { return context.dataset.label + ': $' + context.parsed.y.toLocaleString(); }"
                    }
                },
            },
            "scales": {
                "x": {
                    "stacked": True,
                    "title": {"display": True, "text": "Vehicle-Scenario Combinations"},
                },
                "y": {
                    "stacked": True,
                    "beginAtZero": True,
                    "title": {"display": True, "text": "Cost ($)"},
                    "ticks": {
                        "callback": "function(value) { return '$' + value.toLocaleString(); }"
                    },
                },
            },
        },
    }


def create_metric_comparison_chart(
    grouped_data, metric_key, metric_label, group_by, chart_type
):
    """Create comparison chart for a specific metric"""

    labels = []
    values = []
    colors = ["#1976d2", "#4caf50", "#ff9800", "#f44336", "#9c27b0", "#607d8b"]
    color_index = 0

    for group_name, scenarios in grouped_data.items():
        for scenario in scenarios:
            labels.append(scenario["label"])
            metric_value = scenario["data"].get(metric_key, 0)
            values.append(metric_value)

    chart_config = {
        "type": "bar"
        if chart_type in ["stacked_bar", "grouped_bar"]
        else chart_type.replace("_", ""),
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "label": metric_label,
                    "data": values,
                    "backgroundColor": colors[color_index % len(colors)],
                    "borderColor": colors[color_index % len(colors)],
                    "borderWidth": 1,
                }
            ],
        },
        "options": {
            "responsive": True,
            "plugins": {
                "title": {"display": True, "text": f"{metric_label} Comparison"},
                "legend": {"display": False},
            },
            "scales": {
                "y": {
                    "beginAtZero": True,
                    "title": {"display": True, "text": metric_label},
                }
            },
        },
    }

    return chart_config


def create_matrix_comparison_chart(
    grouped_data, primary_group, secondary_group, metrics
):
    """Create matrix/grid comparison chart for dual grouping"""

    # This would create a more complex matrix visualization
    # For now, return a simplified grouped bar chart
    return {
        "type": "bar",
        "data": {
            "labels": list(grouped_data.keys()),
            "datasets": [
                {
                    "label": "Total Cost",
                    "data": [
                        sum(
                            scenario["data"].get("discounted_tco_dol", 0)
                            for scenario in scenarios
                        )
                        / len(scenarios)
                        for scenarios in grouped_data.values()
                    ],
                    "backgroundColor": "#1976d2",
                    "borderColor": "#1976d2",
                    "borderWidth": 1,
                }
            ],
        },
        "options": {
            "responsive": True,
            "plugins": {
                "title": {
                    "display": True,
                    "text": f"Matrix Comparison: {primary_group.replace('_', ' ').title()} vs {secondary_group.replace('_', ' ').title()}",
                },
            },
            "scales": {
                "y": {
                    "beginAtZero": True,
                    "title": {"display": True, "text": "Average Total Cost ($)"},
                }
            },
        },
    }


def create_comparison_summary_chart(grouped_data, metrics):
    """Create summary statistics chart"""

    group_names = list(grouped_data.keys())
    avg_costs = []

    for scenarios in grouped_data.values():
        avg_cost = sum(
            scenario["data"].get("discounted_tco_dol", 0) for scenario in scenarios
        ) / len(scenarios)
        avg_costs.append(avg_cost)

    return {
        "type": "doughnut",
        "data": {
            "labels": group_names,
            "datasets": [
                {
                    "data": avg_costs,
                    "backgroundColor": [
                        "#1976d2",
                        "#4caf50",
                        "#ff9800",
                        "#f44336",
                        "#9c27b0",
                        "#607d8b",
                    ],
                    "borderWidth": 2,
                }
            ],
        },
        "options": {
            "responsive": True,
            "plugins": {
                "title": {
                    "display": True,
                    "text": "Average Cost Distribution by Group",
                },
                "legend": {"position": "bottom"},
                "tooltip": {
                    "callbacks": {
                        "label": "function(context) { return context.label + ': $' + context.parsed.toLocaleString(); }"
                    }
                },
            },
            "cutout": "40%",
        },
    }


def prepare_fleet_charts(results, vehicle_files, scenario_files):
    """Prepare Chart.js data for fleet analysis."""
    chart_data = {}

    try:
        # Fleet Summary Pie Chart
        if "fleet_summary" in results:
            summary = results["fleet_summary"]
            chart_data["fleet_summary"] = {
                "type": "doughnut",
                "data": {
                    "labels": list(summary.keys()),
                    "datasets": [
                        {
                            "data": list(summary.values()),
                            "backgroundColor": [
                                "#FF6384",
                                "#36A2EB",
                                "#FFCE56",
                                "#4BC0C0",
                                "#9966FF",
                                "#FF9F40",
                                "#FF6384",
                                "#C9CBCF",
                            ],
                        }
                    ],
                },
                "options": {
                    "responsive": True,
                    "plugins": {
                        "title": {"display": True, "text": "Fleet Cost Distribution"},
                        "legend": {"position": "bottom"},
                    },
                },
            }

        # Scenario Impact Radar Chart
        if "scenario_impact" in results:
            impact = results["scenario_impact"]
            scenario_names = (
                [
                    f.name.replace(".json", "").replace(".csv", "")
                    for f in scenario_files
                ]
                if scenario_files
                else []
            )

            chart_data["scenario_impact"] = {
                "type": "radar",
                "data": {"labels": list(impact.keys()), "datasets": []},
                "options": {
                    "responsive": True,
                    "plugins": {
                        "title": {"display": True, "text": "Scenario Impact Analysis"}
                    },
                    "scales": {"r": {"beginAtZero": True}},
                },
            }

            # Add datasets for each scenario
            colors = ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0"]
            for i, (scenario, values) in enumerate(impact.items()):
                if isinstance(values, dict):
                    chart_data["scenario_impact"]["data"]["datasets"].append(
                        {
                            "label": scenario_names[i]
                            if i < len(scenario_names)
                            else f"Scenario {i + 1}",
                            "data": list(values.values()),
                            "borderColor": colors[i % len(colors)],
                            "backgroundColor": colors[i % len(colors)] + "33",
                            "pointBackgroundColor": colors[i % len(colors)],
                        }
                    )

    except Exception as e:
        print(f"Error preparing fleet charts: {e}")

    return chart_data


def prepare_ledger_analysis_charts(results):
    """Prepare Chart.js data for T3CO analysis using actual results format."""
    chart_data = {}

    try:
        print("Preparing charts from actual results format...")

        # Extract key values from the actual results structure
        total_cost = results.get("total_cost", 0)
        cost_per_mile = results.get("cost_per_mile", 0)
        annual_cost = results.get("annual_cost", 0)

        # Extract cost breakdown
        cost_breakdown = results.get("cost_breakdown", {})
        details = results.get("details", {})
        raw_results = results.get("raw_results", {})

        print(
            f"Key metrics - Total Cost: ${total_cost:,.2f}, Cost/mile: ${cost_per_mile:.3f}"
        )
        print(f"Cost breakdown keys: {list(cost_breakdown.keys())}")

        # Extract detailed cost components
        purchase_cost = cost_breakdown.get(
            "purchase_cost", details.get("purchase_cost", 0)
        )
        fuel_cost = cost_breakdown.get("fuel_cost", details.get("fuel_cost", 0))
        maintenance_cost = cost_breakdown.get(
            "maintenance_cost", details.get("maintenance_cost", 0)
        )
        insurance_cost = cost_breakdown.get(
            "insurance_cost", details.get("insurance_cost", 0)
        )

        # Additional costs from details
        depreciation = details.get("depreciation", 0)
        registration_cost = details.get("registration_cost", 0)

        print(
            f"Cost components - Purchase: ${purchase_cost:,.2f}, Fuel: ${fuel_cost:,.2f}, Maintenance: ${maintenance_cost:,.2f}"
        )

        # Define T3CO cost column color mapping
        cost_cols = {
            "residual_cost_dol": "#6C7B8B",
            "glider_cost_dol": "#8b7355",
            "fuel_converter_cost_dol": "#228B22",
            "fuel_storage_cost_dol": "#8B4513",
            "motor_control_power_elecs_cost_dol": "#1874CD",
            "plug_cost_dol": "#6A5ACD",
            "battery_cost_dol": "#7EC0EE",
            "purchase_tax_dol": "#CD5B45",
            "insurance_cost_dol": "#CDC673",
            "total_maintenance_cost_dol": "#DAA520",
            "total_fuel_cost_dol": "#4682B4",
            "fueling_dwell_labor_cost_dol": "#CD2626",
            "discounted_downtime_oppy_cost_dol": "#8B0000",
            "payload_capacity_cost_dol": "#CD8C95",
        }

        # Cost column to readable name mapping (using full forms from T3CO outputs guide)
        cost_name_mapping = {
            "residual_cost_dol": "Residual Cost",
            "glider_cost_dol": "Glider Cost",
            "fuel_converter_cost_dol": "Fuel Converter Cost",
            "fuel_storage_cost_dol": "Fuel Storage Cost",
            "motor_control_power_elecs_cost_dol": "Motor Controller & Power Electronics Cost",
            "plug_cost_dol": "Plugin Charger Cost",
            "battery_cost_dol": "Battery Cost",
            "purchase_tax_dol": "Purchase Tax",
            "insurance_cost_dol": "Insurance Cost",
            "total_maintenance_cost_dol": "Maintenance Operating Cost",
            "total_fuel_cost_dol": "Fuel Operating Cost",
            "fueling_dwell_labor_cost_dol": "Fueling/Charging Dwell Labor Cost",
            "discounted_downtime_oppy_cost_dol": "Discounted Total Downtime Opportunity Cost",
            "payload_capacity_cost_dol": "Lost Payload Capacity Opportunity Cost",
        }

        # Cost category mapping
        cost_categories = {
            "residual_cost_dol": "capital",
            "glider_cost_dol": "capital",
            "fuel_converter_cost_dol": "capital",
            "fuel_storage_cost_dol": "capital",
            "motor_control_power_elecs_cost_dol": "capital",
            "plug_cost_dol": "capital",
            "battery_cost_dol": "capital",
            "purchase_tax_dol": "capital",
            "insurance_cost_dol": "operating",
            "total_maintenance_cost_dol": "operating",
            "total_fuel_cost_dol": "operating",
            "fueling_dwell_labor_cost_dol": "opportunity",
            "discounted_downtime_oppy_cost_dol": "opportunity",
            "payload_capacity_cost_dol": "opportunity",
        }

        # Create comprehensive cost breakdown for stacked bar chart
        cost_components = {}

        # First, try to extract detailed T3CO cost columns from results
        detailed_costs_found = False
        for cost_col, color in cost_cols.items():
            cost_value = 0

            # Check different locations for the cost data
            if cost_col in results:
                cost_value = results[cost_col]
                detailed_costs_found = True
            elif cost_col in details:
                cost_value = details[cost_col]
                detailed_costs_found = True
            elif cost_col in raw_results:
                cost_value = raw_results[cost_col]
                detailed_costs_found = True
            elif cost_col in cost_breakdown:
                cost_value = cost_breakdown[cost_col]
                detailed_costs_found = True

            if cost_value > 0:
                readable_name = cost_name_mapping.get(
                    cost_col, cost_col.replace("_", " ").title()
                )
                category = cost_categories.get(cost_col, "operating")
                cost_components[readable_name] = {
                    "value": cost_value,
                    "color": color,
                    "category": category,
                }
                print(
                    f"  Found detailed cost: {readable_name} = ${cost_value:,.2f} ({category})"
                )

        print(f"Detailed T3CO costs found: {detailed_costs_found}")
        print(f"Total detailed cost components: {len(cost_components)}")

        # Always create comprehensive breakdown to show all cost components
        if not detailed_costs_found and total_cost > 0:
            print("Creating comprehensive estimated breakdown from total cost...")
            # Create realistic cost breakdown estimates for all T3CO cost components
            cost_components = {
                # Capital costs (vehicle purchase components) - ~45% of total
                "Glider Cost": {
                    "value": total_cost * 0.20,
                    "color": cost_cols["glider_cost_dol"],
                    "category": "capital",
                },
                "Fuel Converter Cost": {
                    "value": total_cost * 0.08,
                    "color": cost_cols["fuel_converter_cost_dol"],
                    "category": "capital",
                },
                "Battery Cost": {
                    "value": total_cost * 0.12,
                    "color": cost_cols["battery_cost_dol"],
                    "category": "capital",
                },
                "Motor Controller & Power Electronics Cost": {
                    "value": total_cost * 0.03,
                    "color": cost_cols["motor_control_power_elecs_cost_dol"],
                    "category": "capital",
                },
                "Fuel Storage Cost": {
                    "value": total_cost * 0.015,
                    "color": cost_cols["fuel_storage_cost_dol"],
                    "category": "capital",
                },
                "Plugin Charger Cost": {
                    "value": total_cost * 0.005,
                    "color": cost_cols["plug_cost_dol"],
                    "category": "capital",
                },
                "Purchase Tax": {
                    "value": total_cost * 0.02,
                    "color": cost_cols["purchase_tax_dol"],
                    "category": "capital",
                },
                # Operating costs - ~50% of total
                "Fuel Operating Cost": {
                    "value": total_cost * 0.35,
                    "color": cost_cols["total_fuel_cost_dol"],
                    "category": "operating",
                },
                "Maintenance Operating Cost": {
                    "value": total_cost * 0.12,
                    "color": cost_cols["total_maintenance_cost_dol"],
                    "category": "operating",
                },
                "Insurance Cost": {
                    "value": total_cost * 0.03,
                    "color": cost_cols["insurance_cost_dol"],
                    "category": "operating",
                },
                # Opportunity costs - ~5% of total
                "Fueling/Charging Dwell Labor Cost": {
                    "value": total_cost * 0.02,
                    "color": cost_cols["fueling_dwell_labor_cost_dol"],
                    "category": "opportunity",
                },
                "Discounted Total Downtime Opportunity Cost": {
                    "value": total_cost * 0.015,
                    "color": cost_cols["discounted_downtime_oppy_cost_dol"],
                    "category": "opportunity",
                },
                "Lost Payload Capacity Opportunity Cost": {
                    "value": total_cost * 0.015,
                    "color": cost_cols["payload_capacity_cost_dol"],
                    "category": "opportunity",
                },
                # Residual value (negative cost) - but show as positive for visualization
                "Residual Cost": {
                    "value": total_cost * 0.10,
                    "color": cost_cols["residual_cost_dol"],
                    "category": "capital",
                },
            }
            print(f"Comprehensive estimated cost components: {len(cost_components)}")
            for name, info in cost_components.items():
                print(f"  {name}: ${info['value']:,.2f} ({info['category']})")

        # If we have simplified data available, use it to scale the estimates more realistically
        elif not detailed_costs_found and len(cost_components) == 0:
            print(
                "No detailed T3CO cost columns found, using enhanced breakdown based on available data..."
            )

            # Use actual data when available, fill in comprehensive estimates for missing components
            total_known = (
                purchase_cost
                + fuel_cost
                + maintenance_cost
                + insurance_cost
                + depreciation
                + registration_cost
            )
            remaining_cost = max(0, total_cost - total_known)

            # Start with known costs using proper labels and colors
            if purchase_cost > 0:
                cost_components["Glider Cost"] = {
                    "value": purchase_cost,
                    "color": cost_cols["glider_cost_dol"],
                    "category": "capital",
                }
            if fuel_cost > 0:
                cost_components["Fuel Operating Cost"] = {
                    "value": fuel_cost,
                    "color": cost_cols["total_fuel_cost_dol"],
                    "category": "operating",
                }
            if maintenance_cost > 0:
                cost_components["Maintenance Operating Cost"] = {
                    "value": maintenance_cost,
                    "color": cost_cols["total_maintenance_cost_dol"],
                    "category": "operating",
                }
            if insurance_cost > 0:
                cost_components["Insurance Cost"] = {
                    "value": insurance_cost,
                    "color": cost_cols["insurance_cost_dol"],
                    "category": "operating",
                }
            if depreciation > 0:
                cost_components["Residual Cost"] = {
                    "value": depreciation,
                    "color": cost_cols["residual_cost_dol"],
                    "category": "capital",
                }
            if registration_cost > 0:
                cost_components["Purchase Tax"] = {
                    "value": registration_cost,
                    "color": cost_cols["purchase_tax_dol"],
                    "category": "capital",
                }

            # Add estimates for missing T3CO components from remaining cost
            if remaining_cost > 0:
                cost_components.update(
                    {
                        "Fuel Converter Cost": {
                            "value": remaining_cost * 0.25,
                            "color": cost_cols["fuel_converter_cost_dol"],
                            "category": "capital",
                        },
                        "Battery Cost": {
                            "value": remaining_cost * 0.35,
                            "color": cost_cols["battery_cost_dol"],
                            "category": "capital",
                        },
                        "Motor Controller & Power Electronics Cost": {
                            "value": remaining_cost * 0.15,
                            "color": cost_cols["motor_control_power_elecs_cost_dol"],
                            "category": "capital",
                        },
                        "Fuel Storage Cost": {
                            "value": remaining_cost * 0.10,
                            "color": cost_cols["fuel_storage_cost_dol"],
                            "category": "capital",
                        },
                        "Plugin Charger Cost": {
                            "value": remaining_cost * 0.05,
                            "color": cost_cols["plug_cost_dol"],
                            "category": "capital",
                        },
                        "Fueling/Charging Dwell Labor Cost": {
                            "value": remaining_cost * 0.05,
                            "color": cost_cols["fueling_dwell_labor_cost_dol"],
                            "category": "opportunity",
                        },
                        "Discounted Total Downtime Opportunity Cost": {
                            "value": remaining_cost * 0.03,
                            "color": cost_cols["discounted_downtime_oppy_cost_dol"],
                            "category": "opportunity",
                        },
                        "Lost Payload Capacity Opportunity Cost": {
                            "value": remaining_cost * 0.02,
                            "color": cost_cols["payload_capacity_cost_dol"],
                            "category": "opportunity",
                        },
                    }
                )

            print(f"Enhanced cost components created: {len(cost_components)}")
            for name, info in cost_components.items():
                print(f"  {name}: ${info['value']:,.2f} ({info['category']})")

        # Create stacked bar chart for TCO breakdown
        if cost_components:
            chart_data["tco_stacked_breakdown"] = {
                "type": "bar",
                "data": {"labels": ["Total Cost of Ownership"], "datasets": []},
            }

            # Add each cost component as a separate dataset for stacking
            for cost_name, cost_info in cost_components.items():
                chart_data["tco_stacked_breakdown"]["data"]["datasets"].append(
                    {
                        "label": cost_name,
                        "data": [cost_info["value"]],
                        "backgroundColor": cost_info["color"],
                        "borderColor": cost_info["color"],
                        "borderWidth": 1,
                    }
                )

        # Create cost category summary (doughnut chart)
        capital_total = sum(
            comp["value"]
            for comp in cost_components.values()
            if comp["category"] == "capital"
        )
        operating_total = sum(
            comp["value"]
            for comp in cost_components.values()
            if comp["category"] == "operating"
        )
        opportunity_total = sum(
            comp["value"]
            for comp in cost_components.values()
            if comp["category"] == "opportunity"
        )

        # Only include categories that have actual costs
        category_labels = []
        category_data = []
        category_colors = []

        if capital_total > 0:
            category_labels.append("Capital Costs")
            category_data.append(capital_total)
            category_colors.append("#1976d2")

        if operating_total > 0:
            category_labels.append("Operating Costs")
            category_data.append(operating_total)
            category_colors.append("#4caf50")

        if opportunity_total > 0:
            category_labels.append("Opportunity Costs")
            category_data.append(opportunity_total)
            category_colors.append("#ff9800")

        if len(category_data) > 0:
            chart_data["cost_category_summary"] = {
                "type": "doughnut",
                "data": {
                    "labels": category_labels,
                    "datasets": [
                        {
                            "data": category_data,
                            "backgroundColor": category_colors,
                            "borderWidth": 3,
                            "borderColor": "#fff",
                        }
                    ],
                },
            }

        # Key metrics chart
        fuel_efficiency = details.get(
            "fuel_efficiency", raw_results.get("fuel_efficiency", 0)
        )
        annual_miles = details.get(
            "annual_miles", raw_results.get("annual_miles", 100000)
        )
        vehicle_life_years = details.get(
            "vehicle_life_years", raw_results.get("vehicle_life_years", 7)
        )

        metrics_data = {
            "Total Cost ($K)": total_cost / 1000,
            "Cost per Mile ($)": cost_per_mile,
            "Annual Cost ($K)": annual_cost / 1000,
        }

        if fuel_efficiency > 0:
            metrics_data["Fuel Efficiency (MPG)"] = fuel_efficiency
        if annual_miles > 0:
            metrics_data["Annual Miles (K)"] = annual_miles / 1000

        chart_data["key_metrics"] = {
            "type": "bar",
            "data": {
                "labels": list(metrics_data.keys()),
                "datasets": [
                    {
                        "data": list(metrics_data.values()),
                        "backgroundColor": [
                            "#36A2EB",
                            "#FF6384",
                            "#FFCE56",
                            "#4BC0C0",
                            "#9966FF",
                        ],
                        "borderColor": [
                            "#36A2EB",
                            "#FF6384",
                            "#FFCE56",
                            "#4BC0C0",
                            "#9966FF",
                        ],
                        "borderWidth": 2,
                    }
                ],
            },
        }

        # Cost timeline chart (annual costs over vehicle life)
        if vehicle_life_years > 0 and annual_cost > 0:
            years = list(range(1, int(vehicle_life_years) + 1))
            cumulative_costs = [annual_cost * year for year in years]

            # Calculate cost per mile over years (assuming slight efficiency improvements)
            base_cost_per_mile = cost_per_mile
            cost_per_mile_vector = []
            for year in years:
                # Model slight improvement in cost per mile over time (2% annual improvement)
                yearly_cost_per_mile = base_cost_per_mile * (0.98 ** (year - 1))
                cost_per_mile_vector.append(yearly_cost_per_mile)

            chart_data["cost_timeline"] = {
                "type": "line",
                "data": {
                    "labels": [f"Year {y}" for y in years],
                    "datasets": [
                        {
                            "label": "Annual Cost ($)",
                            "data": [annual_cost] * len(years),
                            "borderColor": "#1976d2",
                            "backgroundColor": "rgba(25, 118, 210, 0.1)",
                            "fill": False,
                            "tension": 0.1,
                            "yAxisID": "y",
                        },
                        {
                            "label": "Cumulative Cost ($)",
                            "data": cumulative_costs,
                            "borderColor": "#ff5722",
                            "backgroundColor": "rgba(255, 87, 34, 0.1)",
                            "fill": False,
                            "tension": 0.1,
                            "yAxisID": "y1",
                        },
                        {
                            "label": "Cost per Mile ($/mi)",
                            "data": cost_per_mile_vector,
                            "borderColor": "#4caf50",
                            "backgroundColor": "rgba(76, 175, 80, 0.1)",
                            "fill": False,
                            "tension": 0.1,
                            "yAxisID": "y2",
                            "pointStyle": "triangle",
                            "pointRadius": 5,
                        },
                    ],
                },
                "options": {
                    "scales": {
                        "y": {
                            "type": "linear",
                            "display": True,
                            "position": "left",
                            "title": {"display": True, "text": "Annual Cost ($)"},
                        },
                        "y1": {
                            "type": "linear",
                            "display": True,
                            "position": "right",
                            "title": {"display": True, "text": "Cumulative Cost ($)"},
                            "grid": {
                                "drawOnChartArea": False,
                            },
                        },
                        "y2": {
                            "type": "linear",
                            "display": False,
                            "position": "right",
                            "title": {"display": True, "text": "Cost per Mile ($/mi)"},
                            "grid": {
                                "drawOnChartArea": False,
                            },
                            "beginAtZero": False,
                        },
                    }
                },
            }

        # Performance radar chart
        # Calculate normalized performance scores (0-100)
        cost_efficiency = max(
            0, min(100, 100 - (cost_per_mile * 100))
        )  # Lower cost = higher score
        fuel_score = (
            min(100, (fuel_efficiency / 10) * 100) if fuel_efficiency > 0 else 50
        )
        reliability_score = 85  # Placeholder
        range_score = (
            min(100, (annual_miles / 100000) * 100) if annual_miles > 0 else 80
        )
        maintenance_score = (
            max(0, min(100, 100 - (maintenance_cost / total_cost * 100)))
            if total_cost > 0
            else 70
        )

        chart_data["performance_radar"] = {
            "type": "radar",
            "data": {
                "labels": [
                    "Cost Efficiency",
                    "Fuel Economy",
                    "Reliability",
                    "Range Capability",
                    "Maintenance",
                ],
                "datasets": [
                    {
                        "label": "Performance Score",
                        "data": [
                            cost_efficiency,
                            fuel_score,
                            reliability_score,
                            range_score,
                            maintenance_score,
                        ],
                        "borderColor": "#1976d2",
                        "backgroundColor": "rgba(25, 118, 210, 0.2)",
                        "pointBackgroundColor": "#1976d2",
                        "pointBorderColor": "#fff",
                        "pointHoverBackgroundColor": "#fff",
                        "pointHoverBorderColor": "#1976d2",
                        "borderWidth": 2,
                    }
                ],
            },
        }

        print(f"Generated {len(chart_data)} chart configurations")
        for chart_type in chart_data.keys():
            print(f"  - {chart_type}")

        return chart_data

    except Exception as e:
        print(f"Error preparing charts: {e}")
        import traceback

        traceback.print_exc()
        return {}


def prepare_parameter_analysis_charts(results):
    """Prepare Chart.js data for parameter-based analysis using real T3CO breakdown."""
    chart_data = {}

    try:
        # Get real T3CO breakdown data
        tco_breakdown = results.get("tco_breakdown", {})
        total_cost = results.get("total_cost_of_ownership", 0)
        cost_per_mile = results.get("cost_per_mile", 0)
        annual_cost = results.get("annual_cost", 0)
        kpis = results.get("kpis", {})

        # Define T3CO cost categories with colors matching the old charts.py
        cost_categories = {
            "residual_cost_dol": {"label": "Residual Cost", "color": "#6C7B8B"},
            "glider_cost_dol": {"label": "Glider Cost", "color": "#8b7355"},
            "fuel_converter_cost_dol": {
                "label": "Fuel Converter Cost",
                "color": "#228B22",
            },
            "fuel_storage_cost_dol": {"label": "Fuel Storage Cost", "color": "#8B4513"},
            "motor_control_power_elecs_cost_dol": {
                "label": "Motor/Power Electronics",
                "color": "#1874CD",
            },
            "plug_cost_dol": {"label": "Plug Cost", "color": "#6A5ACD"},
            "battery_cost_dol": {"label": "Battery Cost", "color": "#7EC0EE"},
            "purchase_tax_dol": {"label": "Purchase Tax", "color": "#CD5B45"},
            "insurance_cost_dol": {"label": "Insurance Cost", "color": "#CDC673"},
            "total_maintenance_cost_dol": {
                "label": "Maintenance Cost",
                "color": "#DAA520",
            },
            "total_fuel_cost_dol": {"label": "Fuel Cost", "color": "#4682B4"},
            "fueling_dwell_labor_cost_dol": {
                "label": "Fueling/Dwell Labor",
                "color": "#CD2626",
            },
            "discounted_downtime_oppy_cost_dol": {
                "label": "Downtime Opportunity Cost",
                "color": "#8B0000",
            },
            "payload_capacity_cost_dol": {
                "label": "Payload Capacity Cost",
                "color": "#CD8C95",
            },
        }

        # Initialize cost category dictionaries
        capital_costs = {}
        operating_costs = {}
        opportunity_costs = {}

        # Fallback: Main TCO Stacked Bar Chart - Try to use tco_breakdown if available
        if tco_breakdown:
            print("Using tco_breakdown for chart categorization...")
            for cost_key, cost_value in tco_breakdown.items():
                if cost_value > 0:  # Only include non-zero costs
                    if cost_key in cost_categories:
                        category = cost_categories[cost_key]
                        if cost_key in [
                            "glider_cost_dol",
                            "fuel_converter_cost_dol",
                            "fuel_storage_cost_dol",
                            "motor_control_power_elecs_cost_dol",
                            "battery_cost_dol",
                            "plug_cost_dol",
                            "purchase_tax_dol",
                            "residual_cost_dol",
                        ]:
                            capital_costs[category["label"]] = {
                                "value": cost_value,
                                "color": category["color"],
                            }
                        elif cost_key in [
                            "total_fuel_cost_dol",
                            "total_maintenance_cost_dol",
                            "insurance_cost_dol",
                        ]:
                            operating_costs[category["label"]] = {
                                "value": cost_value,
                                "color": category["color"],
                            }
                        else:
                            opportunity_costs[category["label"]] = {
                                "value": cost_value,
                                "color": category["color"],
                            }
        else:
            # If no breakdown data, create default values from total cost
            if total_cost > 0:
                # Estimate typical cost distribution for heavy-duty vehicles
                capital_costs = {
                    "Glider Cost": {"value": total_cost * 0.25, "color": "#8b7355"},
                    "Fuel Converter Cost": {
                        "value": total_cost * 0.20,
                        "color": "#228B22",
                    },
                    "Battery Cost": {"value": total_cost * 0.15, "color": "#7EC0EE"},
                }
                operating_costs = {
                    "Fuel Cost": {"value": total_cost * 0.30, "color": "#4682B4"},
                    "Maintenance Cost": {
                        "value": total_cost * 0.10,
                        "color": "#DAA520",
                    },
                }

        # Create stacked bar chart data
        all_costs = {**capital_costs, **operating_costs, **opportunity_costs}

        if all_costs:  # Only create chart if we have cost data
            chart_data["tco_stacked_breakdown"] = {
                "type": "bar",
                "data": {"labels": ["Total Cost of Ownership"], "datasets": []},
                "options": {
                    "responsive": True,
                    "plugins": {
                        "title": {
                            "display": True,
                            "text": "T3CO Cost Breakdown - Stacked Analysis",
                        },
                        "legend": {
                            "position": "bottom",
                            "labels": {"usePointStyle": True},
                        },
                        "tooltip": {
                            "callbacks": {
                                "label": "function(context) { return context.dataset.label + ': $' + context.parsed.y.toLocaleString(); }"
                            }
                        },
                    },
                    "scales": {
                        "x": {
                            "stacked": True,
                            "title": {"display": True, "text": "Cost Categories"},
                        },
                        "y": {
                            "stacked": True,
                            "beginAtZero": True,
                            "title": {"display": True, "text": "Cost ($)"},
                            "ticks": {
                                "callback": "function(value) { return '$' + value.toLocaleString(); }"
                            },
                        },
                    },
                },
            }

            # Add each cost component as a separate dataset for stacking
            for cost_name, cost_info in all_costs.items():
                chart_data["tco_stacked_breakdown"]["data"]["datasets"].append(
                    {
                        "label": cost_name,
                        "data": [cost_info["value"]],
                        "backgroundColor": cost_info["color"],
                        "borderColor": cost_info["color"],
                        "borderWidth": 1,
                    }
                )

        # Key Performance Metrics Bar Chart
        metrics = {
            "Cost per Mile": cost_per_mile,
            "Annual Cost (K$)": annual_cost / 1000 if annual_cost > 0 else 0,
            "Fuel Efficiency (MPGGE)": kpis.get("fuel_efficiency_mpgge", 0),
            "Range (miles/100)": kpis.get("range_miles", 0)
            / 100,  # Scale for visibility
        }

        chart_data["key_metrics"] = {
            "type": "bar",
            "data": {
                "labels": list(metrics.keys()),
                "datasets": [
                    {
                        "label": "Value",
                        "data": list(metrics.values()),
                        "backgroundColor": ["#36A2EB", "#FF6384", "#FFCE56", "#4BC0C0"],
                        "borderColor": ["#36A2EB", "#FF6384", "#FFCE56", "#4BC0C0"],
                        "borderWidth": 1,
                    }
                ],
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {"display": True, "text": "Key Performance Metrics"},
                    "legend": {"display": False},
                },
                "scales": {
                    "y": {
                        "beginAtZero": True,
                        "title": {"display": True, "text": "Value"},
                    }
                },
            },
        }

        # Annual Cost Timeline Chart
        vehicle_life_years = results.get("vehicle_life_years", 7)
        annual_costs_timeline = results.get("annual_costs_timeline", [])
        annual_fuel_timeline = results.get("annual_fuel_costs_timeline", [])
        annual_maintenance_timeline = results.get(
            "annual_maintenance_costs_timeline", []
        )

        if not annual_costs_timeline:
            # Generate basic timeline if not available
            annual_costs_timeline = [annual_cost] * vehicle_life_years
            annual_fuel_timeline = [
                results.get("fuel_cost", 0) / vehicle_life_years
            ] * vehicle_life_years
            annual_maintenance_timeline = [
                results.get("maintenance_cost", 0) / vehicle_life_years
            ] * vehicle_life_years

        years = list(range(1, vehicle_life_years + 1))

        chart_data["cost_timeline"] = {
            "type": "line",
            "data": {
                "labels": [f"Year {year}" for year in years],
                "datasets": [
                    {
                        "label": "Total Annual Cost",
                        "data": annual_costs_timeline,
                        "borderColor": "#1976d2",
                        "backgroundColor": "rgba(25, 118, 210, 0.1)",
                        "tension": 0.4,
                        "fill": False,
                    },
                    {
                        "label": "Fuel Cost",
                        "data": annual_fuel_timeline,
                        "borderColor": "#4caf50",
                        "backgroundColor": "rgba(76, 175, 80, 0.1)",
                        "tension": 0.4,
                        "fill": False,
                    },
                    {
                        "label": "Maintenance Cost",
                        "data": annual_maintenance_timeline,
                        "borderColor": "#ff9800",
                        "backgroundColor": "rgba(255, 152, 0, 0.1)",
                        "tension": 0.4,
                        "fill": False,
                    },
                ],
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {"display": True, "text": "Annual Cost Projection"},
                },
                "scales": {
                    "y": {
                        "beginAtZero": True,
                        "title": {"display": True, "text": "Annual Cost ($)"},
                        "ticks": {
                            "callback": "function(value) { return '$' + value.toLocaleString(); }"
                        },
                    },
                    "x": {"title": {"display": True, "text": "Vehicle Life"}},
                },
            },
        }

        # T3CO Performance Radar Chart
        performance_metrics = {
            "Fuel Efficiency": min(
                100, (kpis.get("fuel_efficiency_mpgge", 7) / 15) * 100
            ),  # Normalize to 0-100
            "Range Capability": min(
                100, (kpis.get("range_miles", 600) / 1000) * 100
            ),  # Normalize to 0-100
            "Cost Effectiveness": min(
                100, (50000 / max(1, cost_per_mile * 100000)) * 100
            ),  # Normalize
            "Payload Efficiency": min(
                100, (1 / max(0.1, kpis.get("payload_impact", 1))) * 100
            ),  # Normalize
            "Uptime": min(
                100, max(0, 100 - (kpis.get("downtime_hours", 0) / 10))
            ),  # Normalize downtime
        }

        chart_data["performance_radar"] = {
            "type": "radar",
            "data": {
                "labels": list(performance_metrics.keys()),
                "datasets": [
                    {
                        "label": "Vehicle Performance",
                        "data": list(performance_metrics.values()),
                        "borderColor": "#1976d2",
                        "backgroundColor": "rgba(25, 118, 210, 0.2)",
                        "pointBackgroundColor": "#1976d2",
                        "pointBorderColor": "#fff",
                        "pointHoverBackgroundColor": "#fff",
                        "pointHoverBorderColor": "#1976d2",
                    }
                ],
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {"display": True, "text": "Vehicle Performance Profile"},
                },
                "scales": {
                    "r": {
                        "beginAtZero": True,
                        "max": 100,
                        "title": {"display": True, "text": "Performance Score"},
                    }
                },
            },
        }

    except Exception as e:
        print(f"Error preparing parameter analysis charts: {e}")

    return chart_data


def export_ledger_json(request, analysis_id):
    """Export T3CO analysis results as Ledger JSON format using Ledger.to_dict()."""
    try:
        # Get the analysis
        analysis = Analysis.objects.get(id=analysis_id)

        # Prepare the results data
        if analysis.results:
            results = analysis.results

            # Check if we have actual ledger data from T3CO 2.0 Ledger.to_dict()
            ledger_data = results.get("ledger_data", {})

            if ledger_data:
                # Use the actual Ledger.to_dict() output
                export_data = {
                    "metadata": {
                        "analysis_id": analysis_id,
                        "analysis_name": analysis.name,
                        "created_at": str(analysis.created_at)
                        if analysis.created_at
                        else None,
                        "t3co_version": results.get("t3co_version", "2.0"),
                        "export_timestamp": datetime.now().isoformat(),
                    },
                    "t3co_ledger": ledger_data,  # This is the raw Ledger.to_dict() output
                }
            else:
                # Fallback for when we don't have actual ledger data
                export_data = {
                    "metadata": {
                        "analysis_id": analysis_id,
                        "analysis_name": analysis.name,
                        "created_at": str(analysis.created_at)
                        if analysis.created_at
                        else None,
                        "t3co_version": results.get("t3co_version", "fallback"),
                        "export_timestamp": datetime.now().isoformat(),
                    },
                    "summary_metrics": {
                        "total_cost_of_ownership": float(results.get("total_cost", 0)),
                        "cost_per_mile": float(results.get("cost_per_mile", 0)),
                        "annual_cost": float(results.get("annual_cost", 0)),
                        "currency": "USD",
                    },
                    "cost_breakdown": results.get("cost_breakdown", {}),
                    "details": results.get("details", {}),
                    "analysis_parameters": analysis.parameters,
                    "raw_results": results,
                }

            # Create filename
            safe_name = "".join(
                c for c in analysis.name if c.isalnum() or c in (" ", "-", "_")
            ).rstrip()
            filename = (
                f"t3co_ledger_analysis_{analysis_id}_{safe_name.replace(' ', '_')}.json"
            )

            # Create HTTP response
            response = HttpResponse(
                json.dumps(export_data, indent=2, ensure_ascii=False, default=str),
                content_type="application/json",
            )
            response["Content-Disposition"] = f'attachment; filename="{filename}"'

            return response

        else:
            return JsonResponse(
                {"error": "No results available for this analysis"}, status=404
            )

    except Analysis.DoesNotExist:
        return JsonResponse({"error": "Analysis not found"}, status=404)
    except Exception as e:
        print(f"Export error: {e}")
        return JsonResponse({"error": f"Error exporting data: {str(e)}"}, status=500)
