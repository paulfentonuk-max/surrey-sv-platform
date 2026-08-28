from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
# Models removed - using only TimestampMixin
from sv_platform.apps.communities.models import CommunityProfile
from sv_platform.apps.impact.models import Intervention, SRICalculation, FinancialProxy, OutcomeMetric
from sv_platform.apps.commitments.models import SVCommitment, Supplier
from sv_platform.apps.activities.models import ActivitySubmission, GeneratedActivity
from sv_platform.apps.projects.models import GeneratedProject
from sv_platform.apps.ai_engine.services import ActivityAnalysisService, ActivityGenerationService, ProjectGenerationService

class CommunityDataViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'])
    def ingest(self, request):
        ingester = CommunityDataIngester()
        count = ingester.ingest_all()
        return Response({'processed': count, 'status': 'complete'})
    
    @action(detail=True, methods=['post'])
    def add_feedback(self, request, pk=None):
        profile = get_object_or_404(CommunityProfile, pk=pk)
        ingester = CommunityDataIngester()
        result = ingester.incorporate_resident_feedback(pk, request.data)
        return Response(result)
    
    @action(detail=True, methods=['get'])
    def emerging_needs(self, request, pk=None):
        ingester = CommunityDataIngester()
        signals = ingester.detect_emerging_needs(pk)
        return Response(signals)

class ActivityAnalysisViewSet(viewsets.ViewSet):
    def create(self, request):
        submission = ActivitySubmission.objects.create(
            input_type=request.data.get('input_type'),
            text_content=request.data.get('text_content', ''),
            media_files=request.data.get('media_files', []),
            submitted_by=request.user,
            community_context_id=request.data.get('community_id')
        )
        service = ActivityAnalysisService()
        analysis = service.analyze_submission(submission)
        
        submission.ai_analysis = analysis
        submission.extracted_activities = analysis.get('activities', [])
        submission.impact_score = analysis.get('impact_score')
        submission.confidence_rating = analysis.get('confidence')
        submission.save()
        
        return Response({
            'submission_id': str(submission.id),
            'analysis': analysis,
            'extracted_activities': submission.extracted_activities
        })

class ActivityGenerationViewSet(viewsets.ViewSet):
    def create(self, request):
        generation = GeneratedActivity.objects.create(
            generation_type=request.data.get('generation_type', 'MIXED'),
            budget_constraint=request.data.get('budget'),
            priority_groups=request.data.get('priority_groups', []),
            created_by=request.user
        )
        for community_id in request.data.get('community_ids', []):
            generation.target_communities.add(community_id)
        
        service = ActivityGenerationService()
        activities = service.generate(generation)
        
        return Response({
            'generation_id': str(generation.id),
            'predicted_sroi': generation.predicted_sroi,
            'activities': activities
        })

class ProjectGenerationViewSet(viewsets.ViewSet):
    def create(self, request):
        activity_id = request.data.get('activity_id')
        activity = get_object_or_404(GeneratedActivity, pk=activity_id)
        
        user_requirements = {
            'purpose': request.data.get('purpose'),
            'scope': request.data.get('scope'),
            'constraints': request.data.get('constraints', []),
            'success_criteria': request.data.get('success_criteria', [])
        }
        
        service = ProjectGenerationService()
        docs = service.generate_project(activity, user_requirements)
        
        project = GeneratedProject.objects.create(
            project_reference=f"SV-{str(activity.id)[:8].upper()}",
            title=activity.selected_activity.get('name', 'New Project') if activity.selected_activity else 'New Project',
            generated_activity=activity,
            user_requirements=user_requirements,
            business_case=docs.get('business_case', {}),
            project_plan=docs.get('project_plan', {}),
            risk_register=docs.get('risk_register', []),
            created_by=request.user
        )
        
        return Response({
            'project_id': str(project.id),
            'project_reference': project.project_reference,
            'documents': docs
        })

class SROICalculatorViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'])
    def calculate(self, request):
        intervention_id = request.data.get('intervention_id')
        intervention = get_object_or_404(Intervention, pk=intervention_id)
        
        calculation, created = SRICalculation.objects.get_or_create(
            intervention=intervention,
            defaults={
                'total_investment': intervention.total_cost,
                'calculation_methodology': 'SROI Standard v2.0',
                'evidence_standards': ['HACT', 'Social_Value_Portal', 'Surrey_HWB']
            }
        )
        
        for metric_data in request.data.get('outcomes', []):
            proxy, _ = FinancialProxy.objects.get_or_create(
                outcome_name=metric_data['outcome_name'],
                defaults={
                    'category': metric_data.get('category', 'COMMUNITY'),
                    'financial_value_gbp': metric_data['value'],
                    'value_basis': metric_data.get('evidence', 'Standard proxy')
                }
            )
            
            metric = OutcomeMetric.objects.create(
                intervention=intervention,
                financial_proxy=proxy,
                quantity=metric_data['quantity'],
                measurement_method=metric_data.get('method', 'Self-reported'),
                deadweight=metric_data.get('deadweight', 0),
                displacement=metric_data.get('displacement', 0),
                attribution=metric_data.get('attribution', 1.0)
            )
            calculation.outcome_metrics.add(metric)
        
        ratio = calculation.calculate()
        
        return Response({
            'sroi_ratio': ratio,
            'total_value': float(calculation.total_social_value),
            'breakdown': calculation.cost_benefit_analysis
        })

class VectorSearchViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'])
    def find_similar_communities(self, request):
        from sentence_transformers import SentenceTransformer
        import numpy as np
        
        target_id = request.data.get('community_id')
        target = get_object_or_404(CommunityProfile, pk=target_id)
        
        if not target.profile_embedding:
            model = SentenceTransformer('all-MiniLM-L6-v2')
            text = f"{target.geographic_area.name} {' '.join(target.emerging_needs_flags)}"
            query_embedding = model.encode(text)
        else:
            query_embedding = np.array(target.profile_embedding)
        
        all_profiles = CommunityProfile.objects.exclude(id=target_id).filter(
            profile_embedding__isnull=False
        )
        
        similarities = []
        for profile in all_profiles:
            other_embedding = np.array(profile.profile_embedding)
            similarity = np.dot(query_embedding, other_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(other_embedding)
            )
            similarities.append({
                'community_id': str(profile.id),
                'name': profile.geographic_area.name,
                'similarity_score': float(similarity),
                'disadvantage_score': profile.composite_disadvantage_score
            })
        
        similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return Response({
            'target_community': target.geographic_area.name,
            'similar_communities': similarities[:10]
        })
