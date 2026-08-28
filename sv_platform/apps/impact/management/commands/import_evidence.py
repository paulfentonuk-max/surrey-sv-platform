from django.core.management.base import BaseCommand
from sv_platform.apps.impact.models import EvidenceSource


class Command(BaseCommand):
    help = 'Import evidence sources from SCC URL list'
    
    SOURCES = [
        {'code': 'TFL-2024-001', 'title': 'Technical Note 3: Total vehicle delay in London', 'url': 'https://content.tfl.gov.uk/Technical-Note-3-Total-vehicle-delay-in-London.pdf', 'org': 'Transport for London', 'type': 'Technical Note'},
        {'code': 'UNBOXED-2023-001', 'title': 'UNBOXED Evaluation Technical Methodology', 'url': 'https://unboxed2022.uk/sites/default/files/2023-03/03%20Annex%20-%20UNBOXED%20Evaluation%20Technical%20Methodology.pdf', 'org': 'UNBOXED 2022', 'type': 'Evaluation Report'},
        {'code': 'BEIS-2024-001', 'title': 'Valuation of Greenhouse Gas Emissions', 'url': 'https://www.gov.uk/government/publications/valuing-greenhouse-gas-emissions-in-policy-appraisal/valuation-of-greenhouse-gas-emissions-for-policy-appraisal-and-evaluation', 'org': 'UK Government (BEIS)', 'type': 'Policy Guidance'},
        {'code': 'YST-001', 'title': 'Value of School Sport', 'url': 'https://www.youthsporttrust.org/media/o1ulxcan/value-of-school-sport-youth-sport-trust-and-state-of-life.pdf', 'org': 'Youth Sport Trust', 'type': 'Research Report'},
        {'code': 'SE-2024-001', 'title': 'Social Value of Sport and Physical Activity 2023-24', 'url': 'https://sportengland-production-files.s3.eu-west-2.amazonaws.com/s3fs-public/2025-11/Social%20value%20of%20sport%20and%20physical%20activity%202023-24%20-%20summary%20report..pdf', 'org': 'Sport England', 'type': 'Research Report', 'year': 2024},
        {'code': 'GOVUK-2024-001', 'title': 'Loneliness Monetisation Report', 'url': 'https://www.gov.uk/government/publications/loneliness-monetisation-report', 'org': 'UK Government', 'type': 'Research Report'},
        {'code': 'MOJ-2024-001', 'title': 'Economic and Social Costs of Reoffending', 'url': 'https://www.gov.uk/government/publications/economic-and-social-costs-of-reoffending', 'org': 'Ministry of Justice', 'type': 'Government Report'},
        {'code': 'NASP-001', 'title': 'Impact of Social Prescribing on Health Service Use', 'url': 'https://socialprescribingacademy.org.uk/nasps-evidence-reports/the-impact-of-social-prescribing-on-health-service-use-and-costs/', 'org': 'National Academy for Social Prescribing', 'type': 'Research Report'},
        {'code': 'SVE-2016-001', 'title': 'Cost of Late Intervention - Technical Report', 'url': 'https://social-value-engine.co.uk/calculator/ASBcost-of-late-intervention-2016_technical-report.pdf', 'org': 'Social Value Engine', 'type': 'Technical Report', 'year': 2016},
    ]
    
    def handle(self, *args, **options):
        for src in self.SOURCES:
            obj, created = EvidenceSource.objects.get_or_create(
                reference_code=src['code'],
                defaults={
                    'title': src['title'],
                    'url': src['url'],
                    'organisation': src['org'],
                    'document_type': src['type'],
                    'publication_year': src.get('year'),
                    'full_citation': f"{src['org']}. {src['title']}. {src.get('year', 'n.d.')}.",
                }
            )
            self.stdout.write(self.style.SUCCESS(f"{'Created' if created else 'Exists'}: {src['code']}"))
