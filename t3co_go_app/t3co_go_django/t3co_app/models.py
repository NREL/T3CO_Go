from django.db import models
from django.utils import timezone


class Vehicle(models.Model):
    """Vehicle model for storing vehicle configurations."""

    name = models.CharField(max_length=200)
    vehicle_type = models.CharField(
        max_length=50,
        choices=[
            ("conventional", "Conventional ICE"),
            ("hybrid", "Hybrid Electric"),
            ("plugin_hybrid", "Plug-in Hybrid"),
            ("battery_electric", "Battery Electric"),
            ("fuel_cell", "Fuel Cell Electric"),
            ("other", "Other"),
        ],
    )
    fuel_type = models.CharField(max_length=50)
    purchase_cost = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    maintenance_cost = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    lifespan = models.IntegerField(help_text="Lifespan in years", null=True, blank=True)
    description = models.TextField(blank=True)
    file_path = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class Scenario(models.Model):
    """Scenario model for storing analysis scenarios."""

    name = models.CharField(max_length=200)
    scenario_type = models.CharField(
        max_length=50,
        choices=[
            ("urban", "Urban Delivery"),
            ("highway", "Highway Transport"),
            ("mixed", "Mixed Use"),
            ("long_haul", "Long Haul"),
            ("regional", "Regional"),
            ("custom", "Custom Scenario"),
        ],
    )
    description = models.TextField(blank=True)
    file_path = models.CharField(max_length=500, blank=True)
    parameters = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class Analysis(models.Model):
    """Analysis model for storing T3CO analysis results."""

    ANALYSIS_TYPES = [
        ("single", "Single Vehicle"),
        ("comparison", "Vehicle Comparison"),
        ("fleet", "Fleet Analysis"),
        ("demo", "Demo Analysis"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("running", "Running"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    name = models.CharField(max_length=200)
    analysis_type = models.CharField(max_length=20, choices=ANALYSIS_TYPES)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="completed"
    )

    # File references
    vehicle_file = models.CharField(max_length=500, blank=True)
    scenario_file = models.CharField(max_length=500, blank=True)

    # Analysis results stored as JSON
    results = models.JSONField(default=dict)

    # Additional parameters
    parameters = models.JSONField(default=dict, blank=True)

    # Relationships
    vehicles = models.ManyToManyField(Vehicle, blank=True)
    scenarios = models.ManyToManyField(Scenario, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.get_analysis_type_display()})"

    def save(self, *args, **kwargs):
        if self.status == "completed" and not self.completed_at:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)

    @property
    def duration(self):
        """Calculate analysis duration."""
        if self.completed_at:
            return self.completed_at - self.created_at
        return None

    @property
    def total_cost(self):
        """Extract total cost from results."""
        if isinstance(self.results, dict):
            return self.results.get("total_cost")
        return None

    @property
    def cost_per_mile(self):
        """Extract cost per mile from results."""
        if isinstance(self.results, dict):
            return self.results.get("cost_per_mile")
        return None


# Legacy model for backward compatibility
class TCOAnalysis(models.Model):
    """Legacy TCO Analysis model."""

    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE)
    total_cost_of_ownership = models.DecimalField(max_digits=15, decimal_places=2)
    analysis_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"TCO Analysis for {self.scenario.name} on {self.analysis_date}"
