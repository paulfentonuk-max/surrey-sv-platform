from django.db import models
from django.db.models import JSONField
from django.contrib.postgres.fields import ArrayField
import uuid
from sv_platform.apps.core.models import TimestampMixin
from sv_platform.apps.communities.models import CommunityProfile

class ActivitySubmission(TimestampMixin):
    INPUT_TYPES = [
        ('IMAGE', 'Image Upload'),
        ('TEXT', 'Text Description'),
        ('VOICE', 'Voice Recording'),
        ('MIXED', 'Mixed Media'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    input_type = models.CharField(max_length=10, choices=INPUT_TYPES)
    text_content = models.TextField(blank=True)
    media_files = ArrayField(models.CharField(max_length=500), default=list)
    audio_transcript = models.TextField(blank=True)
    submitted_by = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    community_context = models.ForeignKey(CommunityProfile, on_delete=models.SET_NULL, null=True)
    ai_analysis = models.JSONField(default=dict)
    extracted_activities = JSONField(default=list)
    estimated_impact = JSONField(default=dict)
    impact_score = models.FloatField(null=True, blank=True)
    confidence_rating = models.FloatField(null=True, blank=True)
    recommended_actions = ArrayField(models.CharField(max_length=300), default=list)
    
    class Meta:
        ordering = ['-created_at']

class GeneratedActivity(TimestampMixin):
    GENERATION_TYPES = [
        ('PREVENTATIVE', 'Preventative Focus'),
        ('SVROI', 'Maximum Social Value ROI'),
        ('MIXED', 'Balanced Approach'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    generation_type = models.CharField(max_length=15, choices=GENERATION_TYPES)
    target_communities = models.ManyToManyField(CommunityProfile)
    budget_constraint = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    priority_groups = ArrayField(models.CharField(max_length=100), default=list)
    ai_prompt = models.TextField()
    generated_activities = JSONField(default=list)
    predicted_sroi = models.FloatField(null=True)
    expected_preventative_impact = models.FloatField(null=True)
    risk_mitigation_score = models.FloatField(null=True)
    selected_activity = models.JSONField(null=True, blank=True)
    selection_rationale = models.TextField(blank=True)
