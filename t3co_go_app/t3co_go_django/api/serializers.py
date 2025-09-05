from rest_framework import serializers
from t3co_app.models import TCOAnalysis, Vehicle, Scenario

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'

class ScenarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scenario
        fields = '__all__'

class TCOAnalysisSerializer(serializers.ModelSerializer):
    vehicle = VehicleSerializer()
    scenario = ScenarioSerializer()

    class Meta:
        model = TCOAnalysis
        fields = '__all__'