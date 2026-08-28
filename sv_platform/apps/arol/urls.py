from django.urls import path
from .views import AROLDashboardView, AROLPatentEvidenceExport, AROLDetailedMetricsView

urlpatterns = [
    path('dashboard/', AROLDashboardView.as_view(), name='arol-dashboard'),
    path('metrics/detailed/', AROLDetailedMetricsView.as_view(), name='arol-detailed'),
    path('patent-evidence/', AROLPatentEvidenceExport.as_view(), name='arol-patent-evidence'),
]
