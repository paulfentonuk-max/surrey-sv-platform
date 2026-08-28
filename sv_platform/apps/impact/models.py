from django.db import models
from django.db.models import JSONField
from django.contrib.postgres.fields import ArrayField
import uuid
from sv_platform.apps.core.models import TimestampMixin
from sv_platform.apps.communities.models import CommunityProfile

class FinancialProxy(TimestampMixin):
    """
    Accredited financial values for social outcomes
    Based on HACT, Social Value Portal, and Surrey-specific standards
    """
    OUTCOME_CATEGORIES = [
        ('EMPLOYMENT', 'Employment & Skills'),
        ('HEALTH', 'Health & Wellbeing'),
        ('COMMUNITY', 'Community Cohesion'),
        ('ENVIRONMENT', 'Environmental'),
        ('DIGITAL', 'Digital Inclusion'),
        ('HOUSING', 'Housing Stability'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.CharField(max_length=20, choices=OUTCOME_CATEGORIES)
    outcome_name = models.CharField(max_length=200)
    description = models.TextField()
    
    financial_value_gbp = models.DecimalField(max_digits=10, decimal_places=2)
    value_basis = models.TextField()
    confidence_interval = JSONField(default=dict)
    validity_period_years = models.IntegerField(default=3)
    
    surrey_hwb_alignment = models.BooleanField(default=False)
    nhs_business_recommendation = models.BooleanField(default=False)
    
    # Framework and evidence fields
    FRAMEWORK_CHOICES = [
        ('SCC', 'Surrey County Council'),
        ('GLOBAL', 'Global/Other Frameworks'),
        ('TOMS', 'National TOMs Framework'),
        ('NI', 'Northern Ireland Specific'),
    ]
    framework = models.CharField(max_length=20, choices=FRAMEWORK_CHOICES, default='GLOBAL')
    evidence_match = models.CharField(max_length=100, blank=True)
    evidence_note = models.TextField(blank=True)
    research_batch = models.CharField(max_length=50, blank=True)
    evidence_url = models.URLField(blank=True, null=True)
    
    # Evidence linking
    evidence_sources = models.ManyToManyField('EvidenceSource', blank=True, related_name='proxies')
    evidence_notes = models.TextField(blank=True)
    geographic_scope = models.CharField(max_length=50, blank=True)
    data_year = models.IntegerField(null=True, blank=True)
    unit_of_measure = models.CharField(max_length=100, blank=True)
    evidence_url = models.URLField(blank=True, null=True, help_text="Direct link to evidence source")
    
    class Meta:
        verbose_name_plural = "Financial Proxies"
    
    def __str__(self):
        return f"{self.outcome_name}: £{self.financial_value_gbp}"

class Intervention(TimestampMixin):
    """Projects and activities delivering social value"""
    INTERVENTION_TYPES = [
        ('PREVENTATIVE', 'Preventative Service'),
        ('TREATMENT', 'Treatment Service'),
        ('COMMUNITY', 'Community Development'),
        ('DIGITAL', 'Digital Inclusion'),
        ('EMPLOYMENT', 'Employment Support'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=300)
    description = models.TextField()
    intervention_type = models.CharField(max_length=20, choices=INTERVENTION_TYPES)
    
    target_communities = models.ManyToManyField(CommunityProfile, related_name='interventions')
    target_groups = ArrayField(models.CharField(max_length=100), default=list)
    
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)
    cost_breakdown = JSONField(default=dict)
    
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    evaluation_status = models.CharField(
        max_length=20,
        choices=[('PLANNED', 'Planned'), ('ACTIVE', 'Active'), ('COMPLETE', 'Complete'), ('EVALUATED', 'Evaluated')],
        default='PLANNED'
    )
    
    def __str__(self):
        return self.title

class OutcomeMetric(TimestampMixin):
    """Measured changes from interventions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    intervention = models.ForeignKey(Intervention, on_delete=models.CASCADE, related_name='outcomes')
    financial_proxy = models.ForeignKey(FinancialProxy, on_delete=models.PROTECT)
    
    quantity = models.IntegerField()
    measurement_method = models.TextField()
    evidence_links = ArrayField(models.CharField(max_length=500), default=list)
    
    verified_by = models.CharField(max_length=200, blank=True)
    verification_date = models.DateField(null=True, blank=True)
    
    deadweight = models.FloatField(default=0.0)
    displacement = models.FloatField(default=0.0)
    attribution = models.FloatField(default=1.0)
    
    @property
    def adjusted_quantity(self):
        return self.quantity * (1 - self.deadweight) * (1 - self.displacement) * self.attribution

class SRICalculation(TimestampMixin):
    """Social Return on Investment calculations"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    intervention = models.OneToOneField(Intervention, on_delete=models.CASCADE, related_name='sroi')
    
    total_investment = models.DecimalField(max_digits=12, decimal_places=2)
    
    total_social_value = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    sroi_ratio = models.FloatField(null=True)
    cost_benefit_analysis = JSONField(default=dict)
    
    calculation_methodology = models.TextField()
    evidence_standards = ArrayField(models.CharField(max_length=100), default=list)
    audit_trail = JSONField(default=list)
    
    def calculate(self):
        total_value = sum(
            metric.adjusted_quantity * float(metric.financial_proxy.financial_value_gbp)
            for metric in self.intervention.outcomes.all()
        )
        
        self.total_social_value = total_value
        self.sroi_ratio = float(total_value) / float(self.total_investment) if self.total_investment else 0
        
        self.cost_benefit_analysis = {
            'investment': float(self.total_investment),
            'return': float(total_value),
            'net_value': float(total_value) - float(self.total_investment),
        }
        self.save()
        return self.sroi_ratio

class PredictiveResourceOptimizer(TimestampMixin):
    """ML-powered resource allocation recommendations"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    target_area = models.ForeignKey(CommunityProfile, on_delete=models.CASCADE)
    intervention_type = models.CharField(max_length=50)
    
    projected_outcomes = JSONField(default=dict)
    confidence_score = models.FloatField()
    similar_interventions = ArrayField(models.CharField(max_length=100), default=list)
    
    recommended_budget = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    optimal_targeting = JSONField(default=dict)
    expected_sroi = models.FloatField(null=True)
    
    actual_outcomes = JSONField(null=True, blank=True)
    prediction_accuracy = models.FloatField(null=True, blank=True)
class EvidenceSource(models.Model):
    """Master bibliography of evidence sources"""
    reference_code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=500)
    organisation = models.CharField(max_length=255)
    url = models.URLField()
    publication_year = models.IntegerField(null=True, blank=True)
    document_type = models.CharField(max_length=50)
    full_citation = models.TextField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['reference_code']
    
    def __str__(self):
        return f"{self.reference_code}: {self.title[:50]}"


# Add to existing FinancialProxy class - run migrations after
# These fields need to be added to FinancialProxy:
# evidence_sources = models.ManyToManyField(EvidenceSource, blank=True)
# evidence_notes = models.TextField(blank=True)
# geographic_scope = models.CharField(max_length=50, blank=True)
# data_year = models.IntegerField(null=True, blank=True)
# unit_of_measure = models.CharField(max_length=100, blank=True)
    evidence_url = models.URLField(blank=True, null=True, help_text="Direct link to evidence source")

class Conversation(models.Model):
    """
    Store AI chat conversations for users
    """
    user_id = models.CharField(max_length=255, db_index=True)  # For now, use session-based ID
    title = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.title or 'Untitled'} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class Message(models.Model):
    """
    Individual messages within a conversation
    """
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20)  # 'user' or 'assistant'
    content = models.TextField()
    proxies_used = models.JSONField(default=list, blank=True)  # Store proxy data
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."
class VCSEResult(models.Model):
    user_id = models.CharField(max_length=100)
    project_name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Step 1: Volunteer Typology
    volunteer_typology = models.CharField(max_length=50)
    
    # Step 2: Prevention Level
    prevention_level = models.CharField(max_length=50)
    
    # Step 3: Beneficiaries
    beneficiary_count = models.IntegerField()
    baseline_situation = models.TextField()
    
    # Step 4: Evidence & Additionality
    evidence_level = models.CharField(max_length=10)
    deadweight = models.IntegerField()
    attribution = models.IntegerField()
    displacement = models.IntegerField()
    dropoff = models.IntegerField()
    
    # Step 5: Calculated Results
    social_value = models.IntegerField()
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.project_name} - £{self.social_value:,}"
# Living Evidence Base Models

class EvidenceItem(models.Model):
    """Core evidence from research, user contributions, or AI discovery"""
    
    SOURCE_CHOICES = [
        ('academic', 'Academic Research'),
        ('government', 'Government Report'),
        ('charity', 'Charity Evaluation'),
        ('user', 'User Contribution'),
        ('ai_discovered', 'AI Discovered'),
    ]
    
    EVIDENCE_QUALITY = [
        ('A', 'A - Strong (RCT, Meta-analysis)'),
        ('B', 'B - Good (Controlled study)'),
        ('C', 'C - Moderate (Before/after)'),
        ('D', 'D - Limited (Case study)'),
    ]
    
    title = models.CharField(max_length=500)
    source_type = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    source_url = models.URLField(blank=True)
    publisher = models.CharField(max_length=200)  # e.g., "University of Surrey", "Gov.uk"
    publication_date = models.DateField()
    
    # Content
    abstract = models.TextField()
    full_text = models.TextField(blank=True)
    key_findings = models.JSONField(default=list)  # List of key points
    
    # Categorization
    intervention_type = models.CharField(max_length=100)  # e.g., "Mental Health Support"
    target_group = models.CharField(max_length=100)  # e.g., "Young People 16-24"
    outcome_measures = models.JSONField(default=list)  # ["Wellbeing", "Employment"]
    
    # Quality & Confidence
    evidence_quality = models.CharField(max_length=1, choices=EVIDENCE_QUALITY, default='C')
    confidence_score = models.FloatField(default=0.0)  # 0.0 to 1.0
    sample_size = models.IntegerField(null=True, blank=True)
    
    # Surrey Context
    is_surrey_specific = models.BooleanField(default=False)
    surrey_area = models.CharField(max_length=100, blank=True)  # Guildford, Woking, etc.
    
    # Metrics
    sroi_ratio = models.CharField(max_length=20, blank=True)  # "4.2:1"
    cost_per_person = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # AI & System
    embedding_vector = models.JSONField(default=list)  # For semantic search
    extracted_keywords = models.JSONField(default=list)
    ai_summary = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    view_count = models.IntegerField(default=0)
    citation_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-confidence_score', '-publication_date']
    
    def __str__(self):
        return f"{self.title[:60]}... ({self.evidence_quality})"


class UserContribution(models.Model):
    """Anonymized user project contributions"""
    
    CONTRIBUTION_STATUS = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    # Anonymized - no personal data
    contribution_id = models.CharField(max_length=50, unique=True)
    user_hash = models.CharField(max_length=64)  # Anonymized user identifier
    
    # Project Details
    project_type = models.CharField(max_length=100)
    intervention_category = models.CharField(max_length=100)
    target_demographic = models.CharField(max_length=100)
    surrey_area = models.CharField(max_length=100, blank=True)
    
    # Outcomes
    people_reached = models.IntegerField()
    outcomes_achieved = models.JSONField(default=list)
    sroi_calculated = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    
    # Lessons
    what_worked = models.TextField()
    what_didnt = models.TextField()
    key_lessons = models.TextField()
    
    # Status
    status = models.CharField(max_length=20, choices=CONTRIBUTION_STATUS, default='pending')
    reviewed_by = models.CharField(max_length=100, blank=True)
    review_notes = models.TextField(blank=True)
    
    # Converted to EvidenceItem
    evidence_item = models.ForeignKey(EvidenceItem, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Contribution {self.contribution_id[:8]}... ({self.status})"


class AIResearchLog(models.Model):
    """Log of AI research activities"""
    
    RESEARCH_TYPE = [
        ('scheduled', 'Scheduled Update'),
        ('query_triggered', 'Query Triggered'),
        ('manual', 'Manual Search'),
    ]
    
    research_type = models.CharField(max_length=20, choices=RESEARCH_TYPE)
    query_used = models.TextField()
    sources_searched = models.JSONField(default=list)
    items_found = models.IntegerField(default=0)
    items_added = models.IntegerField(default=0)
    
    # Quality metrics
    avg_confidence = models.FloatField(null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.research_type} - {self.items_added} items added"


class EvidenceQueryLog(models.Model):
    """Track what users search for to identify gaps"""
    
    query_text = models.TextField()
    results_found = models.IntegerField()
    user_clicked_results = models.JSONField(default=list)
    satisfaction_rating = models.IntegerField(null=True, blank=True)  # 1-5
    
    # Gap identification
    results_were_sufficient = models.BooleanField(default=True)
    suggested_new_evidence = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Query: {self.query_text[:50]}..."


