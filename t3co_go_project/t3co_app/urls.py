from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path("", views.dashboard, name="dashboard"),
    # Analysis views
    path("analysis/", views.tco_analysis, name="tco_analysis"),
    path(
        "analysis/parameters/",
        views.tco_parameter_analysis,
        name="tco_parameter_analysis",
    ),
    path(
        "analysis/parameters/<int:analysis_id>/results/",
        views.parameter_analysis_results,
        name="parameter_analysis_results",
    ),
    path(
        "analysis/parameters/<int:analysis_id>/export-ledger/",
        views.export_ledger_json,
        name="export_ledger_json",
    ),
    path("comparison/", views.vehicle_comparison, name="vehicle_comparison"),
    path("fleet/", views.fleet_analysis, name="fleet_analysis"),
    # Results and details
    path("analysis/<int:analysis_id>/", views.analysis_detail, name="analysis_detail"),
    # Data management
    path("vehicles/", views.vehicle_list, name="vehicle_list"),
    path("scenarios/", views.scenario_list, name="scenario_list"),
    # Demo and utilities
    path("demo/", views.demo_data, name="demo_data"),
    path("demo/run/", views.run_demo_analysis, name="run_demo_analysis"),
    path(
        "demo/parameter-results/",
        views.demo_parameter_results,
        name="demo_parameter_results",
    ),
    path("debug/charts/", views.debug_charts, name="debug_charts"),
    # AJAX endpoints
    path(
        "api/vehicle-parameters/",
        views.get_vehicle_parameters,
        name="get_vehicle_parameters",
    ),
    # Legacy URLs for backward compatibility
    path("results/", views.results, name="results"),
    path("analysis/legacy/", views.analysis, name="analysis_legacy"),
]
