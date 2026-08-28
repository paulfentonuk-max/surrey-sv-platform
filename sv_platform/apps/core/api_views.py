from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from ..communities.models import CommunityProfile
from ..impact.models import FinancialProxy, Intervention, SRICalculation
from ..activities.models import ActivitySubmission, GeneratedActivity
from ..arol.models import AIRequestLog
from .surrey_i_client import SurreyIClient

@api_view(['GET'])
def dashboard_stats(request):
    """Return dashboard statistics"""
    return Response({
        'total_social_value': 2400000,
        'active_communities': CommunityProfile.objects.filter(status='ACTIVE').count(),
        'sroi_ratio': 4.2,
        'arol_efficiency': 68,
        'recent_activity': [
            {'title': 'Community Garden Project', 'type': 'Activity Analysis', 'time': '2 hours ago'},
            {'title': 'Youth Employment Initiative', 'type': 'SROI Calculation', 'time': '4 hours ago'},
        ]
    })

@api_view(['GET', 'POST'])
def communities_list(request):
    """List all communities or create new"""
    if request.method == 'GET':
        communities = CommunityProfile.objects.all()
        data = [{
            'id': str(c.id),
            'name': c.geographic_area.name,
            'postcode': c.geographic_area.code,
            'deprivation_score': c.composite_disadvantage_score,
            'health_index': c.health_inequality_index,
            'status': c.status,
        } for c in communities]
        return Response(data)
    
    elif request.method == 'POST':
        # Create new community from postcode data
        data = request.data
        # Implementation here
        return Response({'status': 'created'}, status=201)

@api_view(['POST'])
def fetch_surrey_i_data(request):
    """Fetch Surrey-i data for LSOA"""
    lsoa_code = request.data.get('lsoa_code')
    if not lsoa_code:
        return Response({'error': 'LSOA code required'}, status=400)
    
    client = SurreyIClient()
    data = client.get_area_data(lsoa_code)
    
    return Response(data)

@api_view(['GET'])
def financial_proxies_list(request):
    """Return all financial proxies"""
    proxies = FinancialProxy.objects.all()
    data = [{
        'id': str(p.id),
        'name': p.outcome_name,
        'category': p.category,
        'value': float(p.financial_value_gbp),
    } for p in proxies]
    return Response(data)

@api_view(['POST'])
def calculate_sroi(request):
    """Calculate SROI for intervention"""
    data = request.data
    # Implementation
    return Response({
        'sroi_ratio': 4.2,
        'total_value': 180000,
        'total_cost': data.get('total_cost', 50000),
    })

@api_view(['GET'])
def arol_metrics(request):
    """Return AROL monitoring metrics"""
    logs = AIRequestLog.objects.all()
    total_requests = logs.count()
    cache_hits = logs.filter(cache_hit=True).count()
    
    return Response({
        'total_requests': total_requests,
        'cache_hit_rate': (cache_hits / total_requests * 100) if total_requests > 0 else 0,
        'avg_input_reduction': 85.5,
        'total_savings': 1250.00,
    })
