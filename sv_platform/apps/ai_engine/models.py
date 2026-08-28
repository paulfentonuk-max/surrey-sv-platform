from django.db import models
from django.contrib.postgres.fields import JSONField
import uuid
from sv_platform.apps.core.models import TimestampMixin

class AIRequestLog(TimestampMixin):
    REQUEST_TYPES = [
        ('VISION', 'Vision Analysis'),
        ('TEXT', 'Text Analysis'),
        ('VOICE', 'Voice Analysis'),
        ('GENERATION', 'Content Generation'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPES)
    prompt = models.TextField()
    response = models.TextField()
    tokens_used = models.IntegerField()
    cost_usd = models.DecimalField(max_digits=10, decimal_places=6)
    processing_time_ms = models.IntegerField()
    success = models.BooleanField()
    error_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']

class VeniceAIConfig(TimestampMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model_name = models.CharField(max_length=100)
    temperature = models.FloatField(default=0.7)
    max_tokens = models.IntegerField(default=2000)
    top_p = models.FloatField(default=1.0)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.model_name
