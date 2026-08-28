"""
Evidence Linking Tool for Financial Proxies
"""

from sv_platform.apps.impact.models import FinancialProxy


class EvidenceLinker:
    """Tool for linking proxies to evidence sources"""
    
    EVIDENCE_LIBRARY = {
        'sport': [
            {'url': 'https://sportengland-production-files.s3.eu-west-2.amazonaws.com/s3fs-public/2025-11/Social%20value%20of%20sport%20and%20physical%20activity%202023-24%20-%20summary%20report..pdf', 'title': 'Sport England Social Value Report'},
        ],
        'employment': [
            {'url': 'https://www.gov.uk/government/publications/economic-and-social-costs-of-reoffending', 'title': 'MOJ Economic Costs'},
        ],
    }
    
    def suggest_evidence(self, proxy):
        suggestions = []
        text = f"{proxy.outcome_name} {proxy.description} {proxy.category}".lower()
        for keyword, sources in self.EVIDENCE_LIBRARY.items():
            if keyword in text:
                suggestions.extend(sources)
        return suggestions
    
    def get_proxy_list(self):
        proxies = FinancialProxy.objects.all()
        result = []
        for p in proxies:
            result.append({
                'id': str(p.id),
                'name': p.outcome_name,
                'category': p.category,
                'has_evidence': bool(p.evidence_url),
                'evidence_url': p.evidence_url or '',
            })
        return result


def show_proxies_needing_evidence():
    linker = EvidenceLinker()
    proxies = linker.get_proxy_list()
    print(f"\nTotal proxies: {len(proxies)}")
    print(f"Needing evidence: {sum(1 for p in proxies if not p['has_evidence'])}")
    for p in proxies[:5]:
        print(f"\n  {p['name'][:50]}")
        print(f"  Has evidence: {p['has_evidence']}")
