from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .serializers import TCOAnalysisSerializer
from core.t3co_integration import perform_tco_analysis
import os

class TCOAnalysisViewSet(viewsets.ViewSet):
    def create(self, request):
        serializer = TCOAnalysisSerializer(data=request.data)
        if serializer.is_valid():
            vehicle_file = serializer.validated_data.get('vehicle_file')
            scenario_file = serializer.validated_data.get('scenario_file')

            # Ensure files are saved in the demo_inputs directory
            vehicle_path = os.path.join('demo_inputs', 'vehicles', vehicle_file.name)
            scenario_path = os.path.join('demo_inputs', 'scenarios', scenario_file.name)

            with open(vehicle_path, 'wb+') as vehicle_destination:
                for chunk in vehicle_file.chunks():
                    vehicle_destination.write(chunk)

            with open(scenario_path, 'wb+') as scenario_destination:
                for chunk in scenario_file.chunks():
                    scenario_destination.write(chunk)

            # Perform TCO analysis
            results = perform_tco_analysis(vehicle_path, scenario_path)

            return Response(results, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        # Logic to retrieve and return existing analyses can be implemented here
        return Response({"message": "List of TCO analyses will be implemented."}, status=status.HTTP_200_OK)