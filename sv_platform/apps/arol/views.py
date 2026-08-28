from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Avg, Sum, Count, F, Q
from django.utils import timezone
from datetime import timedelta
from .models import AIRequestLog, AROLDashboardMetrics

class AROLDashboardView(APIView):
    """
    Admin-only dashboard for AROL monitoring
    Separate from SV platform user interface
    """
    
    def get(self, request):
        if not request.user.is_staff:
            return Response({'error': 'Admin access required'}, status=403)
        
        last_24h = timezone.now() - timedelta(hours=24)
        
        metrics_24h = AIRequestLog.objects.filter(created_at__gte=last_24h).aggregate(
            total_requests=Count('id'),
            cache_hits=Count('id', filter=Q(cache_hit=True)),
            avg_input_reduction=Avg('input_reduction_percentage'),
            total_savings=Sum('savings_vs_baseline_usd'),
            total_cost=Sum('estimated_cost_usd'),
            avg_response_time=Avg('total_time_ms'),
        )
        
        cache_hit_rate = (
            (metrics_24h['cache_hits'] / metrics_24h['total_requests'] * 100)
            if metrics_24h['total_requests'] > 0 else 0
        )
        
        total_baseline = (metrics_24h['total_cost'] or 0) + (metrics_24h['total_savings'] or 0)
        savings_percent = (
            ((metrics_24h['total_savings'] or 0) / total_baseline * 100)
            if total_baseline > 0 else 0
        )
        
        request_types = AIRequestLog.objects.filter(
            created_at__gte=last_24h
        ).values('request_type').annotate(
            count=Count('id'),
            avg_savings=Avg('savings_vs_baseline_usd'),
        )
        
        trend_data = []
        for i in range(7):
            day_start = timezone.now() - timedelta(days=i+1)
            day_end = timezone.now() - timedelta(days=i)
            
            day_metrics = AIRequestLog.objects.filter(
                created_at__range=(day_start, day_end)
            ).aggregate(
                requests=Count('id'),
                savings=Sum('savings_vs_baseline_usd'),
                cache_hits=Count('id', filter=Q(cache_hit=True)),
            )
            
            trend_data.append({
                'date': day_start.strftime('%Y-%m-%d'),
                'requests': day_metrics['requests'] or 0,
                'savings': float(day_metrics['savings'] or 0),
                'cache_hit_rate': (
                    (day_metrics['cache_hits'] / day_metrics['requests'] * 100)
                    if day_metrics['requests'] > 0 else 0
                ),
            })
        
        return Response({
            'period': '24h',
            'summary': {
                'total_requests': metrics_24h['total_requests'],
                'cache_hit_rate': round(cache_hit_rate, 2),
                'avg_input_reduction': round(metrics_24h['avg_input_reduction'] or 0, 2),
                'total_savings_usd': round(float(metrics_24h['total_savings'] or 0), 4),
                'total_cost_usd': round(float(metrics_24h['total_cost'] or 0), 4),
                'savings_percentage': round(savings_percent, 2),
                'avg_response_time_ms': round(metrics_24h['avg_response_time'] or 0, 2),
            },
            'request_types': list(request_types),
            'trend': trend_data,
        })

class AROLDetailedMetricsView(APIView):
    """Detailed metrics for patent documentation"""
    
    def get(self, request):
        if not request.user.is_staff:
            return Response({'error': 'Admin access required'}, status=403)
        
        days = int(request.GET.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        detailed_metrics = AIRequestLog.objects.filter(
            created_at__gte=start_date
        ).values('request_type').annotate(
            total_requests=Count('id'),
            total_original_size=Sum('original_input_size_bytes'),
            total_optimized_size=Sum('optimized_input_size_bytes'),
            cache_hits=Count('id', filter=Q(cache_hit=True)),
            total_savings=Sum('savings_vs_baseline_usd'),
        )
        
        for metric in detailed_metrics:
            if metric['total_original_size'] and metric['total_original_size'] > 0:
                metric['compression_ratio'] = (
                    metric['total_optimized_size'] / metric['total_original_size']
                )
            else:
                metric['compression_ratio'] = 0
            
            if metric['total_requests'] > 0:
                metric['cache_hit_rate'] = (
                    metric['cache_hits'] / metric['total_requests'] * 100
                )
            else:
                metric['cache_hit_rate'] = 0
        
        return Response({
            'period_days': days,
            'generated_at': timezone.now().isoformat(),
            'metrics': list(detailed_metrics),
            'total_data_processed_mb': sum(
                m['total_original_size'] or 0 for m in detailed_metrics
            ) / (1024 * 1024),
            'total_data_saved_mb': sum(
                (m['total_original_size'] or 0) - (m['total_optimized_size'] or 0)
                for m in detailed_metrics
            ) / (1024 * 1024),
        })

class AROLPatentEvidenceExport(APIView):
    """
    Export metrics in format suitable for patent filing evidence
    """
    
    def get(self, request):
        if not request.user.is_staff:
            return Response({'error': 'Admin access required'}, status=403)
        
        evidence = {
            'invention_title': 'AI Request Optimization Layer (AROL)',
            'filing_date': timezone.now().strftime('%Y-%m-%d'),
            'technical_effects': [],
            'performance_improvements': [],
            'cost_reductions': [],
        }
        
        all_requests = AIRequestLog.objects.all()
        
        if all_requests.exists():
            avg_reduction = all_requests.aggregate(
                Avg('input_reduction_percentage')
            )['input_reduction_percentage__avg']
            
            evidence['technical_effects'].append({
                'effect': 'Data Transfer Minimization',
                'description': 'Reduction in data transferred to AI API',
                'average_percentage': round(avg_reduction, 2),
                'mechanism': 'Image compression, metadata stripping, format optimization',
            })
            
            cache_hits = all_requests.filter(cache_hit=True).count()
            total = all_requests.count()
            cache_rate = (cache_hits / total * 100) if total > 0 else 0
            
            evidence['technical_effects'].append({
                'effect': 'Computational Efficiency Through Caching',
                'description': 'Avoidance of redundant API calls',
                'cache_hit_rate': round(cache_rate, 2),
                'mechanism': 'Semantic content hashing with Redis caching',
            })
            
            total_savings = all_requests.aggregate(
                Sum('savings_vs_baseline_usd')
            )['savings_vs_baseline_usd__sum']
            
            evidence['cost_reductions'].append({
                'metric': 'Total Cost Savings',
                'amount_usd': round(float(total_savings or 0), 2),
                'period': 'All recorded requests',
            })
        
        return Response(evidence)
