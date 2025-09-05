from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.conf import settings
import os

from .forms import TCOAnalysisForm, VehicleComparisonForm, FleetAnalysisForm, TCOAnalysisParameterForm
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
                    
                    context = {
                        "analysis": analysis,
                        "results": results,
                        "chart_data": chart_data,
                        "form": TCOAnalysisParameterForm(),
                        "form_data": form_data,  # Pass back for reference
                    }
                    return render(request, "t3co_app/parameter_analysis_results.html", context)
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


def vehicle_comparison(request):
    """Multi-vehicle comparison analysis with Chart.js visualizations."""
    if request.method == "POST":
        form = VehicleComparisonForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                t3co = T3COIntegration()

                # Get form data
                vehicle_files = request.FILES.getlist("vehicle_files")
                scenario_file = form.cleaned_data["scenario_file"]
                comparison_name = form.cleaned_data["comparison_name"]

                # Save files temporarily
                vehicle_paths = []
                scenario_path = default_storage.save(
                    f"temp/{scenario_file.name}", scenario_file
                )

                for vehicle_file in vehicle_files:
                    path = default_storage.save(
                        f"temp/{vehicle_file.name}", vehicle_file
                    )
                    vehicle_paths.append(os.path.join(settings.MEDIA_ROOT, path))

                scenario_abs_path = os.path.join(settings.MEDIA_ROOT, scenario_path)

                # Run comparison analysis
                results = t3co.perform_tco_analysis(
                    vehicle_files=vehicle_paths, scenario_files=[scenario_abs_path]
                )

                if results and results.get("success"):
                    # Prepare Chart.js comparison data
                    chart_data = prepare_comparison_charts(results, vehicle_files)

                    # Save comparison analysis
                    analysis = Analysis.objects.create(
                        name=comparison_name,
                        analysis_type="comparison",
                        scenario_file=scenario_file.name,
                        results=results,
                    )

                    # Clean up temporary files
                    default_storage.delete(scenario_path)
                    for path in vehicle_paths:
                        rel_path = os.path.relpath(path, settings.MEDIA_ROOT)
                        default_storage.delete(rel_path)

                    context = {
                        "analysis": analysis,
                        "results": results,
                        "chart_data": chart_data,
                        "vehicle_names": [f.name for f in vehicle_files],
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
                    default_storage.delete(scenario_path)
                    for path in vehicle_paths:
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


def prepare_comparison_charts(results, vehicle_files):
    """Prepare Chart.js data for vehicle comparison."""
    chart_data = {}

    try:
        # Vehicle names for labels
        vehicle_names = (
            [f.name.replace(".json", "").replace(".csv", "") for f in vehicle_files]
            if vehicle_files
            else []
        )

        # TCO Comparison Bar Chart
        if "comparison_tco" in results:
            tco_data = results["comparison_tco"]
            chart_data["tco_comparison"] = {
                "type": "bar",
                "data": {
                    "labels": vehicle_names or list(range(1, len(tco_data) + 1)),
                    "datasets": [
                        {
                            "label": "Total Cost of Ownership ($)",
                            "data": tco_data,
                            "backgroundColor": "#36A2EB",
                            "borderColor": "#36A2EB",
                            "borderWidth": 1,
                        }
                    ],
                },
                "options": {
                    "responsive": True,
                    "plugins": {
                        "title": {"display": True, "text": "Vehicle TCO Comparison"}
                    },
                    "scales": {
                        "y": {
                            "beginAtZero": True,
                            "title": {"display": True, "text": "Total Cost ($)"},
                        }
                    },
                },
            }

        # Cost Components Stacked Bar Chart
        if "comparison_breakdown" in results:
            breakdown = results["comparison_breakdown"]
            datasets = []
            colors = ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF", "#FF9F40"]

            for i, (component, values) in enumerate(breakdown.items()):
                datasets.append(
                    {
                        "label": component,
                        "data": values,
                        "backgroundColor": colors[i % len(colors)],
                        "borderColor": colors[i % len(colors)],
                        "borderWidth": 1,
                    }
                )

            chart_data["cost_breakdown_comparison"] = {
                "type": "bar",
                "data": {
                    "labels": vehicle_names or list(range(1, len(values) + 1)),
                    "datasets": datasets,
                },
                "options": {
                    "responsive": True,
                    "plugins": {
                        "title": {"display": True, "text": "Cost Components Comparison"}
                    },
                    "scales": {
                        "x": {"stacked": True},
                        "y": {
                            "stacked": True,
                            "beginAtZero": True,
                            "title": {"display": True, "text": "Cost ($)"},
                        },
                    },
                },
            }

    except Exception as e:
        print(f"Error preparing comparison charts: {e}")

    return chart_data


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


def prepare_parameter_analysis_charts(results):
    """Prepare Chart.js data for parameter-based analysis."""
    chart_data = {}
    
    try:
        # TCO Summary Gauge Chart (using doughnut as approximation)
        total_cost = results.get('total_cost_of_ownership', 0)
        cost_per_mile = results.get('cost_per_mile', 0)
        annual_cost = results.get('annual_cost', 0)
        
        chart_data["tco_summary"] = {
            "type": "doughnut",
            "data": {
                "labels": ["Total TCO", "Remaining Budget"],
                "datasets": [{
                    "data": [total_cost, max(0, 500000 - total_cost)],  # 500k budget example
                    "backgroundColor": ["#FF6384", "#E0E0E0"],
                    "borderWidth": 2,
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {"display": True, "text": f"Total Cost of Ownership: ${total_cost:,.0f}"},
                    "legend": {"display": False},
                },
                "cutout": "60%",
            }
        }
        
        # Cost Breakdown Pie Chart
        cost_components = {
            "Vehicle Purchase": results.get('purchase_cost', 0),
            "Fuel": results.get('fuel_cost', 0),
            "Maintenance": results.get('maintenance_cost', 0),
            "Insurance": results.get('insurance_cost', 0),
            "Registration": results.get('registration_cost', 0),
            "Depreciation": results.get('depreciation', 0)
        }
        
        chart_data["cost_breakdown"] = {
            "type": "pie",
            "data": {
                "labels": list(cost_components.keys()),
                "datasets": [{
                    "data": list(cost_components.values()),
                    "backgroundColor": [
                        "#FF6384", "#36A2EB", "#FFCE56", 
                        "#4BC0C0", "#9966FF", "#FF9F40"
                    ],
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {"display": True, "text": "Cost Breakdown"},
                    "legend": {"position": "bottom"},
                },
            }
        }
        
        # Key Metrics Bar Chart
        metrics = {
            "Cost per Mile": cost_per_mile,
            "Annual Cost": annual_cost / 1000,  # Show in thousands
            "Fuel Efficiency": results.get('fuel_efficiency', 0),
            "Vehicle Life (Years)": results.get('vehicle_life_years', 0)
        }
        
        chart_data["key_metrics"] = {
            "type": "bar",
            "data": {
                "labels": list(metrics.keys()),
                "datasets": [{
                    "label": "Value",
                    "data": list(metrics.values()),
                    "backgroundColor": ["#36A2EB", "#FF6384", "#FFCE56", "#4BC0C0"],
                    "borderColor": ["#36A2EB", "#FF6384", "#FFCE56", "#4BC0C0"],
                    "borderWidth": 1,
                }]
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
            }
        }
        
        # Efficiency Impact Line Chart (showing aero improvement factor over time)
        years = list(range(2025, 2051))  # 2025-2050
        efficiency_timeline = [results.get('fuel_efficiency', 7.0) * (1 + (year - 2025) * 0.01) for year in years]
        
        chart_data["efficiency_timeline"] = {
            "type": "line",
            "data": {
                "labels": years,
                "datasets": [{
                    "label": "Fuel Efficiency (MPG)",
                    "data": efficiency_timeline,
                    "borderColor": "#4BC0C0",
                    "backgroundColor": "rgba(75, 192, 192, 0.1)",
                    "tension": 0.4,
                    "fill": True,
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {"display": True, "text": "Projected Fuel Efficiency Over Time"},
                },
                "scales": {
                    "y": {
                        "beginAtZero": False,
                        "title": {"display": True, "text": "Miles per Gallon"},
                    },
                    "x": {
                        "title": {"display": True, "text": "Year"},
                    }
                },
            }
        }
        
    except Exception as e:
        print(f"Error preparing parameter analysis charts: {e}")
        
    return chart_data
