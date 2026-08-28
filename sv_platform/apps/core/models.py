from django.db import models
from django.contrib.gis.db import models as gis_models
from django.db.models import JSONField
from django.contrib.postgres.fields import ArrayField
import uuid
from django.contrib.auth import get_user_model

User = get_user_model()

class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='+')
    
    class Meta:
        abstract = True

class GeographicArea(TimestampMixin):
    """LSOA/MSOA level geographic areas for Surrey"""
    AREA_TYPES = [
        ('LSOA', 'Lower Layer Super Output Area'),
        ('MSOA', 'Middle Layer Super Output Area'),
        ('WARD', 'Electoral Ward'),
        ('DISTRICT', 'District Council'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    area_type = models.CharField(max_length=20, choices=AREA_TYPES)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    
    # Geometry for mapping
    boundary = gis_models.MultiPolygonField(null=True, blank=True)
    centroid = gis_models.PointField(null=True, blank=True)
    
    # Vector embedding for similarity matching
    embedding = ArrayField(models.FloatField(), null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['area_type', 'code']),
            models.Index(fields=['embedding'], name='embedding_idx'),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.code})"

class EthicalFramework(TimestampMixin):
    """Resident advisory and ethical oversight"""
    FRAMEWORK_TYPES = [
        ('ADVISORY_BOARD', 'Resident Advisory Board'),
        ('PRIVACY_REVIEW', 'Privacy Impact Assessment'),
        ('ALGORITHM_AUDIT', 'Algorithm Audit'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    framework_type = models.CharField(max_length=30, choices=FRAMEWORK_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    resident_representatives = ArrayField(models.CharField(max_length=100))
    meeting_notes = models.JSONField(default=dict)
    approved_recommendations = models.JSONField(default=list)
    
    def __str__(self):
        return self.title
