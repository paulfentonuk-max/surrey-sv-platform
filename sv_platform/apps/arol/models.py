from django.db import models
from django.db.models import JSONField
from django.contrib.postgres.fields import ArrayField
import uuid
from sv_platform.apps.core.models import TimestampMixin

class AIRequestLog(TimestampMixin):
    """Log every AI API call for monitoring and optimization analysis"""
    REQUEST_TYPES = [
        ('VISION', 'Vision Analysis'),
        ('TEXT', 'Text Analysis'),
        ('VOICE', 'Voice Analysis'),
        ('GENERATION', 'Content Generation'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPES)
    
    # Input metrics
    original_input_size_bytes = models.IntegerField()
    optimized_input_size_bytes = models.IntegerField()
    input_reduction_percentage = models.FloatField()
    
    # Token metrics (for text/vision)
    prompt_tokens = models.IntegerField(null=True, blank=True)
    completion_tokens = models.IntegerField(null=True, blank=True)
    total_tokens = models.IntegerField(null=True, blank=True)
    
    # Caching
    cache_hit = models.BooleanField(default=False)
    cache_key = models.CharField(max_length=64, blank=True)
    
    # Performance
    preprocessing_time_ms = models.IntegerField()
    api_response_time_ms = models.IntegerField(null=True, blank=True)
    total_time_ms = models.IntegerField()
    
    # Cost
    estimated_cost_usd = models.DecimalField(max_digits=10, decimal_places=6)
    savings_vs_baseline_usd = models.DecimalField(max_digits=10, decimal_places=6)
    
    # Result
    success = models.BooleanField()
    error_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['request_type', 'created_at']),
            models.Index(fields=['cache_hit']),
        ]

class AROLDashboardMetrics(TimestampMixin):
    """Aggregated metrics for dashboard display"""
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    period_type = models.CharField(max_length=20)
    
    # Volume
    total_requests = models.IntegerField()
    vision_requests = models.IntegerField()
    text_requests = models.IntegerField()
    voice_requests = models.IntegerField()
    generation_requests = models.IntegerField()
    
    # Efficiency
    avg_input_reduction_percent = models.FloatField()
    total_data_saved_mb = models.FloatField()
    cache_hit_rate = models.FloatField()
    
    # Performance
    avg_response_time_ms = models.FloatField()
    avg_preprocessing_time_ms = models.FloatField()
    
    # Cost
    total_estimated_cost_usd = models.DecimalField(max_digits=12, decimal_places=2)
    total_savings_vs_baseline_usd = models.DecimalField(max_digits=12, decimal_places=2)
    savings_percentage = models.FloatField()
    
    class Meta:
        ordering = ['-period_start']
        unique_together = ['period_start', 'period_type']

class AROLOptimizationRule(TimestampMixin):
    """Configurable optimization rules"""
    RULE_TYPES = [
        ('IMAGE_COMPRESSION', 'Image Compression'),
        ('METADATA_STRIPPING', 'Metadata Stripping'),
        ('PROMPT_OPTIMIZATION', 'Prompt Optimization'),
        ('RESPONSE_CACHING', 'Response Caching'),
        ('BATCH_PROCESSING', 'Batch Processing'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    rule_type = models.CharField(max_length=30, choices=RULE_TYPES)
    is_active = models.BooleanField(default=True)
    config = models.JSONField(default=dict)
    times_applied = models.IntegerField(default=0)
    total_savings_generated = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.name} ({self.rule_type})"
