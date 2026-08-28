from rest_framework.decorators import api_view
from rest_framework.response import Response
from .ai_service import analyze_project_input

@api_view(['POST'])
def analyze_project(request):
    """
    Analyze project inputs using Venice AI
    """
    answers = request.data.get('answers', {})
    files = request.data.get('files', [])
    
    # Call Venice AI
    result = analyze_project_input(answers, files)
    
    return Response({
        'success': True,
        'analysis': result['analysis'],
        'recommendations': result['recommendations'],
        'confidence': result['confidence'],
    })
from .models import VCSEResult

@api_view(['POST'])
@permission_classes([AllowAny])
def save_vcse_result(request):
    try:
        data = request.data
        result = VCSEResult.objects.create(
            user_id=data.get('user_id', 'anonymous'),
            project_name=data.get('project_name', 'Untitled Project'),
            volunteer_typology=data.get('volunteer_typology'),
            prevention_level=data.get('prevention_level'),
            beneficiary_count=data.get('beneficiary_count'),
            baseline_situation=data.get('baseline_situation'),
            evidence_level=data.get('evidence_level'),
            deadweight=data.get('deadweight', 20),
            attribution=data.get('attribution', 10),
            displacement=data.get('displacement', 5),
            dropoff=data.get('dropoff', 10),
            social_value=data.get('social_value')
        )
        return Response({'success': True, 'id': result.id})
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def list_vcse_results(request):
    user_id = request.query_params.get('user_id', 'anonymous')
    results = VCSEResult.objects.filter(user_id=user_id)
    data = [{
        'id': r.id,
        'project_name': r.project_name,
        'created_at': r.created_at,
        'social_value': r.social_value,
        'volunteer_typology': r.volunteer_typology,
        'prevention_level': r.prevention_level
    } for r in results]
    return Response({'success': True, 'results': data})
cat >> ~/surrey-sv-platform/sv_platform/apps/impact/api_views.py << 'ENDOFFILE'

# Living Evidence Base API
from .models import EvidenceItem, UserContribution, EvidenceQueryLog
from django.db.models import Q, Count
import uuid

@api_view(['GET'])
@permission_classes([AllowAny])
def search_evidence(request):
    """Semantic search for evidence"""
    query = request.query_params.get('q', '')
    category = request.query_params.get('category', '')
    
    # Simple search (in production, use vector similarity)
    evidence = EvidenceItem.objects.filter(
        Q(title__icontains=query) | 
        Q(abstract__icontains=query) |
        Q(key_findings__icontains=query)
    )
    
    if category:
        evidence = evidence.filter(intervention_type=category)
    
    # Log query for gap analysis
    EvidenceQueryLog.objects.create(
        query_text=query,
        results_found=evidence.count()
    )
    
    data = [{
        'id': e.id,
        'title': e.title,
        'source': e.publisher,
        'quality': e.evidence_quality,
        'sroi': e.sroi_ratio,
        'summary': e.ai_summary or e.abstract[:200] + '...'
    } for e in evidence[:10]]
    
    return Response({'success': True, 'results': data, 'total': evidence.count()})

@api_view(['POST'])
@permission_classes([AllowAny])
def contribute_evidence(request):
    """Users contribute anonymized project results"""
    data = request.data
    
    contribution = UserContribution.objects.create(
        contribution_id=f"UC{uuid.uuid4().hex[:8].upper()}",
        user_hash=data.get('user_hash', 'anonymous'),
        project_type=data.get('project_type'),
        intervention_category=data.get('intervention_category'),
        target_demographic=data.get('target_demographic'),
        surrey_area=data.get('surrey_area', ''),
        people_reached=data.get('people_reached', 0),
        outcomes_achieved=data.get('outcomes_achieved', []),
        sroi_calculated=data.get('sroi_calculated'),
        what_worked=data.get('what_worked', ''),
        what_didnt=data.get('what_didnt', ''),
        key_lessons=data.get('key_lessons', '')
    )
    
    return Response({
        'success': True, 
        'message': 'Thank you! Your contribution is pending review.',
        'contribution_id': contribution.contribution_id
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def get_evidence_gaps(request):
    """AI identifies what evidence is missing based on query logs"""
    # Find queries with few results
    gaps = EvidenceQueryLog.objects.filter(
        results_were_sufficient=False
    ).values('query_text').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    return Response({
        'success': True,
        'gaps': list(gaps),
        'message': 'These topics need more evidence'
    })
ENDOFFILE
