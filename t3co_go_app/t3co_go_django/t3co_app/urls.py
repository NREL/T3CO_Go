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
    # Legacy URLs for backward compatibility
    path("results/", views.results, name="results"),
    path("analysis/legacy/", views.analysis, name="analysis_legacy"),
]
