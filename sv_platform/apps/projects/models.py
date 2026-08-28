from django.db import models
from django.db.models import JSONField
from django.contrib.postgres.fields import ArrayField
import uuid
from sv_platform.apps.core.models import TimestampMixin
from sv_platform.apps.activities.models import GeneratedActivity

class ProjectTemplate(TimestampMixin):
    TEMPLATE_TYPES = [
        ('SMALL', 'Small Project'),
        ('MEDIUM', 'Medium Project'),
        ('LARGE', 'Major Project'),
        ('PROGRAMME', 'Programme'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    template_type = models.CharField(max_length=15, choices=TEMPLATE_TYPES)
    business_case_template = JSONField(default=dict)
    project_initiation_document = JSONField(default=dict)
    project_plan_template = JSONField(default=dict)
    risk_register_template = JSONField(default=dict)
    sv_requirements_section = models.TextField()
    evaluation_framework = JSONField(default=dict)

class GeneratedProject(TimestampMixin):
    PROJECT_STAGES = [
        ('INITIATION', 'Initiation'),
        ('PLANNING', 'Planning'),
        ('EXECUTION', 'Execution'),
        ('MONITORING', 'Monitoring & Control'),
        ('CLOSURE', 'Closure'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project_reference = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=300)
    generated_activity = models.ForeignKey(GeneratedActivity, on_delete=models.SET_NULL, null=True)
    user_requirements = JSONField(default=dict)
    business_case = JSONField(default=dict)
    project_initiation_document = JSONField(default=dict)
    project_plan = JSONField(default=dict)
    resource_plan = JSONField(default=dict)
    risk_register = JSONField(default=list)
    quality_plan = JSONField(default=dict)
    sv_targets = JSONField(default=dict)
    evaluation_plan = JSONField(default=dict)
    current_stage = models.CharField(max_length=20, choices=PROJECT_STAGES, default='INITIATION')
    approval_status = models.CharField(
        max_length=20,
        choices=[('DRAFT', 'Draft'), ('REVIEW', 'Under Review'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')],
        default='DRAFT'
    )
    
    class Meta:
        ordering = ['-created_at']
