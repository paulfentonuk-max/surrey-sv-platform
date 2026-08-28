from django.db import models
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.contrib.postgres.indexes import GinIndex


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


class FinancialProxy(models.Model):
    """Social Value financial proxies"""
    category = models.CharField(max_length=100, db_index=True)
    subcategory = models.CharField(max_length=100, db_index=True)
    proxy_name = models.CharField(max_length=255)
    description = models.TextField()
    unit_of_measure = models.CharField(max_length=100)
    value = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="GBP")
    geographic_scope = models.CharField(max_length=50, db_index=True)
    data_year = models.IntegerField()
    source_organisation = models.CharField(max_length=255)
    evidence_sources = models.ManyToManyField(EvidenceSource, blank=True, related_name='proxies')
    evidence_notes = models.TextField(blank=True)
    confidence_rating = models.CharField(
        max_length=20,
        choices=[
            ('high', 'High - Multiple robust studies'),
            ('medium', 'Medium - Limited but credible evidence'),
            ('low', 'Low - Estimated/proxy values'),
        ],
        default='medium'
    )
    search_vector = SearchVectorField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Financial Proxies"
        indexes = [
            models.Index(fields=['category', 'geographic_scope', 'is_active']),
            models.Index(fields=['subcategory', 'data_year']),
            GinIndex(fields=['search_vector']),
        ]
    
    def __str__(self):
        return f"{self.proxy_name} ({self.unit_of_measure})"
