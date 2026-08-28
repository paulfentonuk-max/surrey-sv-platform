from django.db import models
from django.db.models import JSONField
from django.contrib.postgres.fields import ArrayField
import uuid
from sv_platform.apps.core.models import TimestampMixin, GeographicArea

class CommunityProfile(TimestampMixin):
    """
    Living Community Profile - Dynamic narratives updated through multiple channels
    """
    PROFILE_STATUS = [
        ('ACTIVE', 'Active'),
        ('UNDER_REVIEW', 'Under Review'),
        ('ARCHIVED', 'Archived'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    geographic_area = models.OneToOneField(GeographicArea, on_delete=models.CASCADE, related_name='profile')
    status = models.CharField(max_length=20, choices=PROFILE_STATUS, default='ACTIVE')
    
    # Official Statistics
    census_data = models.JSONField(default=dict)
    deprivation_index = models.JSONField(default=dict)
    health_outcomes = models.JSONField(default=dict)
    
    # Calculated Metrics
    composite_disadvantage_score = models.FloatField(null=True, blank=True)
    health_inequality_index = models.FloatField(null=True, blank=True)
    social_isolation_risk = models.FloatField(null=True, blank=True)
    
    # Community Voice
    resident_surveys = models.JSONField(default=list)
    community_reports = models.JSONField(default=list)
    provider_insights = models.JSONField(default=list)
    
    # Dynamic Narrative
    ai_generated_summary = models.TextField(blank=True)
    emerging_needs_flags = ArrayField(models.CharField(max_length=100), default=list)
    early_warning_signals = models.JSONField(default=dict)
    
    # Vector embedding for similarity matching
    profile_embedding = ArrayField(models.FloatField(), null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['composite_disadvantage_score']),
            models.Index(fields=['profile_embedding'], name='profile_embedding_idx'),
        ]
    
    def calculate_disadvantage_index(self):
        """Weight multiple deprivation factors"""
        weights = {
            'income': 0.25,
            'employment': 0.25,
            'education': 0.15,
            'health': 0.20,
            'crime': 0.10,
            'housing': 0.05
        }
        
        imd = self.deprivation_index
        score = sum(
            imd.get(factor, 0) * weight 
            for factor, weight in weights.items()
        )
        self.composite_disadvantage_score = score
        return score

class ResidentFeedback(TimestampMixin):
    """Qualitative insights quantified alongside official metrics"""
    FEEDBACK_TYPES = [
        ('SURVEY', 'Community Survey'),
        ('MEETING', 'Public Meeting'),
        ('DIGITAL', 'Digital Platform'),
        ('PROVIDER', 'Service Provider Report'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    community_profile = models.ForeignKey(CommunityProfile, on_delete=models.CASCADE, related_name='feedback')
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES)
    source_date = models.DateField()
    
    # Content
    raw_text = models.TextField()
    sentiment_score = models.FloatField(null=True, blank=True)
    extracted_themes = ArrayField(models.CharField(max_length=100), default=list)
    priority_flags = ArrayField(models.CharField(max_length=50), default=list)
    
    # Quantification
    severity_score = models.IntegerField(choices=[(i, i) for i in range(1, 6)], null=True)
    estimated_affected_residents = models.IntegerField(null=True, blank=True)
    
    # AI Analysis
    ai_analysis = models.JSONField(default=dict)
    
    class Meta:
        ordering = ['-source_date']
