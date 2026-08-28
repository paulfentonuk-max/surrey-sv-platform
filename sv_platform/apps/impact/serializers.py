from rest_framework import serializers
from .models import FinancialProxy, EvidenceSource


class EvidenceSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvidenceSource
        fields = ['reference_code', 'title', 'organisation', 'url']


class FinancialProxySerializer(serializers.ModelSerializer):
    value_formatted = serializers.SerializerMethodField()
    framework_display = serializers.CharField(source='get_framework_display', read_only=True)
    
    class Meta:
        model = FinancialProxy
        fields = [
            'id', 'category', 'outcome_name', 'description',
            'unit_of_measure', 'financial_value_gbp', 'value_formatted',
            'framework', 'framework_display',
            'evidence_url', 'evidence_match', 'evidence_note', 
            'research_batch', 'geographic_scope', 'data_year',
            'value_basis', 'validity_period_years'
        ]
    
    def get_value_formatted(self, obj):
        return f"£{obj.financial_value_gbp:,.2f}"
