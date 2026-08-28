from django.contrib import admin
from .models import FinancialProxy, Intervention, OutcomeMetric, SRICalculation, PredictiveResourceOptimizer

@admin.register(FinancialProxy)
class FinancialProxyAdmin(admin.ModelAdmin):
    list_display = ['outcome_name', 'category', 'financial_value_gbp', 'surrey_hwb_alignment']
    list_filter = ['category', 'surrey_hwb_alignment', 'nhs_business_recommendation']
    search_fields = ['outcome_name', 'description']

@admin.register(Intervention)
class InterventionAdmin(admin.ModelAdmin):
    list_display = ['title', 'intervention_type', 'total_cost', 'start_date', 'is_active']
    list_filter = ['intervention_type', 'is_active', 'evaluation_status']

@admin.register(OutcomeMetric)
class OutcomeMetricAdmin(admin.ModelAdmin):
    list_display = ['intervention', 'financial_proxy', 'quantity', 'adjusted_quantity']

@admin.register(SRICalculation)
class SRICalculationAdmin(admin.ModelAdmin):
    list_display = ['intervention', 'sroi_ratio', 'total_social_value']

@admin.register(PredictiveResourceOptimizer)
class PredictiveResourceOptimizerAdmin(admin.ModelAdmin):
    list_display = ['target_area', 'intervention_type', 'expected_sroi', 'confidence_score']
