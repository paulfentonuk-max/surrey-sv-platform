from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from sv_platform.apps.core.views import (
    CommunityDataViewSet, ActivityAnalysisViewSet,
    ActivityGenerationViewSet, ProjectGenerationViewSet,
    SROICalculatorViewSet, VectorSearchViewSet
)
from sv_platform.apps.core.api_views import (
    dashboard_stats, communities_list, fetch_surrey_i_data,
    financial_proxies_list, calculate_sroi, arol_metrics
)

router = DefaultRouter()
router.register(r'communities/data', CommunityDataViewSet, basename='community-data')
router.register(r'activities/analyse', ActivityAnalysisViewSet, basename='activity-analyse')
router.register(r'activities/generate', ActivityGenerationViewSet, basename='activity-generate')
router.register(r'projects/generate', ProjectGenerationViewSet, basename='project-generate')
router.register(r'calculations/sroi', SROICalculatorViewSet, basename='sroi-calc')
router.register(r'search/vectors', VectorSearchViewSet, basename='vector-search')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path('arol/', include('sv_platform.apps.arol.urls')),
    
    # New API endpoints for frontend
    path('api/dashboard/stats/', dashboard_stats, name='dashboard-stats'),
    path('api/communities/list/', communities_list, name='communities-list'),
    path('api/communities/data/fetch_surrey_i_data/', fetch_surrey_i_data, name='fetch-surrey-i'),
    path('api/proxies/list/', financial_proxies_list, name='proxies-list'),
    path('api/sroi/calculate/', calculate_sroi, name='calculate-sroi'),
    path('api/arol/metrics/', arol_metrics, name='arol-metrics'),
]

# Proxy API endpoints
from sv_platform.apps.impact import api_views as impact_api
from rest_framework.routers import DefaultRouter

proxy_router = DefaultRouter()
proxy_router.register(r'proxies', impact_api.FinancialProxyViewSet, basename='proxy')
proxy_router.register(r'evidence-sources', impact_api.EvidenceSourceViewSet, basename='evidence')

urlpatterns += [
    path('api/ai/chat/', impact_api.ai_chat, name='ai_chat'),
    path('api/ai/analyze/', impact_api.ai_analyze, name='ai_analyze'),
    path('api/vcse/save/', impact_api.save_vcse_result, name='save_vcse_result'),
    path('api/vcse/list/', impact_api.list_vcse_results, name='list_vcse_results'),
path('api/evidence/search/', impact_api.search_evidence, name='search_evidence'),
path('api/evidence/contribute/', impact_api.contribute_evidence, name='contribute_evidence'),
path('api/evidence/gaps/', impact_api.get_evidence_gaps, name='get_evidence_gaps'),
    path('api/', include(proxy_router.urls)),
]
