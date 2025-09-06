from django.urls import path
from .views import TCOAnalysisView, TCOResultsView

urlpatterns = [
    path('analysis/', TCOAnalysisView.as_view(), name='tco_analysis'),
    path('results/', TCOResultsView.as_view(), name='tco_results'),
]