import json
from rest_framework import viewsets, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .models import FinancialProxy, EvidenceSource
from .serializers import FinancialProxySerializer, EvidenceSourceSerializer

class FinancialProxyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FinancialProxy.objects.all()
    serializer_class = FinancialProxySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['framework', 'category']
    search_fields = ['outcome_name', 'description']
    pagination_class = None
    
    def get_queryset(self):
        queryset = super().get_queryset()
        framework = self.request.query_params.get('framework', 'ALL')
        if framework and framework != 'ALL':
            queryset = queryset.filter(framework=framework)
        return queryset
    
    @action(detail=False, methods=['get'])
    def frameworks(self, request):
        frameworks = []
        for code, name in FinancialProxy.FRAMEWORK_CHOICES:
            count = FinancialProxy.objects.filter(framework=code).count()
            if count > 0:
                frameworks.append({'code': code, 'name': name, 'count': count})
        total = FinancialProxy.objects.count()
        frameworks.insert(0, {'code': 'ALL', 'name': 'All Frameworks', 'count': total})
        return Response(frameworks)

class EvidenceSourceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EvidenceSource.objects.all()
    serializer_class = EvidenceSourceSerializer

from .ai_service import ai_service

@api_view(['POST'])
@permission_classes([AllowAny])
def ai_chat(request):
    message = request.data.get('message', '')
    conversation_history = request.data.get('history', [])
    
    try:
        # Use enhanced chat with proxy lookup
        result = ai_service.chat_with_proxies(message, conversation_history)
        
        return Response({
            'success': True,
            'response': result['response'],
            'proxies_used': result['proxies_used'],
            'proxies_count': result['proxies_count']
        })
        
    except Exception as e:
        print(f"AI Chat Error: {e}")
        return Response({
            'success': False,
            'response': "I'm experiencing technical difficulties. Please try again."
        }, status=500)
@api_view(['GET'])
@permission_classes([AllowAny])
def search_proxies(request):
    from django.db.models import Q
    query = request.GET.get('q', '')
    proxies = FinancialProxy.objects.all()
    if query:
        proxies = proxies.filter(Q(outcome_name__icontains=query) | Q(category__icontains=query))
    results = proxies.values('id', 'category', 'outcome_name', 'unit_of_measure', 'financial_value_gbp')[:5]
    return Response({'success': True, 'count': len(results), 'results': list(results)})

from .models import Conversation, Message

@api_view(['POST'])
@permission_classes([AllowAny])
def save_conversation(request):
    """
    Save a conversation with messages
    """
    try:
        title = request.data.get('title', 'New Conversation')
        messages_data = request.data.get('messages', [])
        user_id = request.data.get('user_id', 'anonymous')
        
        # Create conversation
        conversation = Conversation.objects.create(
            user_id=user_id,
            title=title[:100]  # Limit title length
        )
        
        # Create messages
        for msg in messages_data:
            Message.objects.create(
                conversation=conversation,
                role=msg.get('role', 'user'),
                content=msg.get('content', ''),
                proxies_used=msg.get('proxies_used', [])
            )
        
        return Response({
            'success': True,
            'conversation_id': conversation.id,
            'message': 'Conversation saved'
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_conversations(request):
    """
    Get list of conversations for a user
    """
    user_id = request.GET.get('user_id', 'anonymous')
    
    conversations = Conversation.objects.filter(user_id=user_id).values(
        'id', 'title', 'created_at', 'updated_at'
    )[:20]  # Last 20 conversations
    
    return Response({
        'success': True,
        'conversations': list(conversations)
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def get_conversation(request, conversation_id):
    """
    Get full conversation with messages
    """
    try:
        conversation = Conversation.objects.get(id=conversation_id)
        messages = conversation.messages.values(
            'role', 'content', 'proxies_used', 'created_at'
        )
        
        return Response({
            'success': True,
            'conversation': {
                'id': conversation.id,
                'title': conversation.title,
                'created_at': conversation.created_at,
                'messages': list(messages)
            }
        })
        
    except Conversation.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Conversation not found'
        }, status=404)

@api_view(['POST'])
@permission_classes([AllowAny])
def ai_analyze(request):
    answers = request.data.get('answers', {})
    
    try:
        # Simple analysis response
        analysis = f"Based on your inputs: {json.dumps(answers, indent=2)}"
        
        recommendations = [
            {
                'type': 'Community Engagement',
                'estimated_sroi': '3.5:1',
                'proxies': ['Social Connection', 'Wellbeing'],
                'rationale': 'High impact for community projects'
            }
        ]
        
        return Response({
            'analysis': analysis,
            'recommendations': recommendations
        })
        
    except Exception as e:
        print(f"AI Analyze Error: {e}")
        return Response({
            'analysis': 'Error processing request',
            'recommendations': []
        }, status=500)
# VCSE Results API
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
# Living Evidence Base API
from .models import EvidenceItem, UserContribution, EvidenceQueryLog

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
        count=models.Count('id')
    ).order_by('-count')[:10]
    
    return Response({
        'success': True,
        'gaps': list(gaps),
        'message': 'These topics need more evidence'
    })
