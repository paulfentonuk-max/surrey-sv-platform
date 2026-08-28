from django.db import models
from django.db.models import JSONField
from django.contrib.postgres.fields import ArrayField
import uuid
from sv_platform.apps.core.models import TimestampMixin

class Supplier(TimestampMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    registration_number = models.CharField(max_length=50, unique=True)
    contact_details = JSONField(default=dict)
    is_scc_contractor = models.BooleanField(default=False)
    contract_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return self.name

class SVCommitment(TimestampMixin):
    COMMITMENT_STATUS = [
        ('PROPOSED', 'Proposed'), ('NEGOTIATED', 'Negotiated'), ('APPROVED', 'Approved'),
        ('IN_PROGRESS', 'In Progress'), ('COMPLETE', 'Complete'), ('VERIFIED', 'Verified'),
    ]
    PRIORITY_AREAS = [
        ('multiple_disadvantage', 'Multiple Disadvantage'),
        ('low_uptake_health', 'Low Uptake of Health Services'),
        ('digital_inclusion', 'Digital Inclusion'),
        ('transport_barriers', 'Transport Barriers'),
        ('disability_access', 'Disability Access'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    commitment_reference = models.CharField(max_length=20, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='commitments')
    target_groups = ArrayField(models.CharField(max_length=50, choices=PRIORITY_AREAS), default=list)
    health_inequality_focuses = ArrayField(models.CharField(max_length=50), default=list)
    description = models.TextField()
    expected_outcomes = JSONField(default=list)
    financial_value = models.DecimalField(max_digits=12, decimal_places=2)
    required_evidence_standards = ArrayField(models.CharField(max_length=100), default=list)
    surrey_hwb_alignment = models.BooleanField(default=False)
    nhs_business_recommendation = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=COMMITMENT_STATUS, default='PROPOSED')
    proposed_date = models.DateField()
    target_completion = models.DateField()
    actual_completion = models.DateField(null=True, blank=True)
    milestones = JSONField(default=list)
    evidence_submitted = JSONField(default=list)
    
    class Meta:
        ordering = ['-proposed_date']
