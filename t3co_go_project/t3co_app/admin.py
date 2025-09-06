from django.contrib import admin
from .models import Vehicle, Scenario, TCOAnalysis

# Register your models here.
admin.site.register(Vehicle)
admin.site.register(Scenario)
admin.site.register(TCOAnalysis)