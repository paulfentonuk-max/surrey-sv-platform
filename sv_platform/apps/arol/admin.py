from django.contrib import admin
from .models import AIRequestLog, AROLDashboardMetrics, AROLOptimizationRule

@admin.register(AIRequestLog)
class AIRequestLogAdmin(admin.ModelAdmin):
    list_display = [
        'request_type', 'original_input_size_bytes', 'optimized_input_size_bytes',
        'input_reduction_percentage', 'cache_hit', 'estimated_cost_usd',
        'savings_vs_baseline_usd', 'success', 'created_at'
    ]
    list_filter = ['request_type', 'cache_hit', 'success', 'created_at']
    readonly_fields = [
        'input_reduction_percentage', 'estimated_cost_usd', 'savings_vs_baseline_usd'
    ]
    date_hierarchy = 'created_at'

@admin.register(AROLDashboardMetrics)
class AROLDashboardMetricsAdmin(admin.ModelAdmin):
    list_display = [
        'period_type', 'period_start', 'total_requests',
        'avg_input_reduction_percent', 'cache_hit_rate',
        'total_savings_vs_baseline_usd', 'savings_percentage'
    ]
    list_filter = ['period_type']

@admin.register(AROLOptimizationRule)
class AROLOptimizationRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'rule_type', 'is_active', 'times_applied', 'total_savings_generated']
    list_filter = ['rule_type', 'is_active']
    list_editable = ['is_active']
