import pdfplumber
import re
from decimal import Decimal
from django.core.management.base import BaseCommand
from sv_platform.apps.impact.models import FinancialProxy, EvidenceSource


class Command(BaseCommand):
    help = 'Import SCC Proxies from PDF table structure'
    
    EVIDENCE_MAP = {
        'greenhouse gas': ['BEIS-2024-001'],
        'carbon': ['BEIS-2024-001'],
        'sport': ['YST-001', 'SE-2024-001'],
        'physical activity': ['SE-2024-001'],
        'loneliness': ['GOVUK-2024-001'],
        'social prescribing': ['NASP-001'],
        'reoffending': ['MOJ-2024-001'],
        'prison': ['MOJ-2024-001'],
        'transport': ['TFL-2024-001'],
        'vehicle': ['TFL-2024-001'],
        'intervention': ['SVE-2016-001'],
        'unboxed': ['UNBOXED-2023-001'],
    }
    
    def match_evidence(self, text):
        text_lower = text.lower()
        matched = []
        for keyword, codes in self.EVIDENCE_MAP.items():
            if keyword in text_lower:
                for code in codes:
                    try:
                        matched.append(EvidenceSource.objects.get(reference_code=code))
                    except:
                        pass
        return list(set(matched))
    
    def extract_table_data(self, page):
        """Extract data from PDF table"""
        tables = page.extract_tables()
        if tables:
            return tables[0]  # First table on page
        return []
    
    def parse_proxy_from_row(self, row, current_category):
        """Parse a table row into proxy data"""
        if not row or len(row) < 3:
            return None
        
        # Clean up cells
        cells = [str(cell).strip() if cell else '' for cell in row]
        
        # Skip header rows
        if any(h in cells[0].lower() for h in ['category', 'proxy', 'organisation', 'print create']):
            return None
        
        # First cell might be category or empty (continuation)
        category = cells[0] if cells[0] and not cells[0].startswith('Proxies') else current_category
        
        # Find proxy description (usually longest text)
        proxy_desc = ''
        organisation = ''
        unit = ''
        
        for cell in cells[1:]:
            if 'Surrey' in cell or 'Global' in cell or 'Council' in cell:
                organisation = cell
            elif 'per' in cell.lower() or 'number of' in cell.lower():
                unit = cell
            elif len(cell) > len(proxy_desc):
                proxy_desc = cell
        
        # Try to extract value from description
        value = None
        value_match = re.search(r'£([\d,]+(?:\.\d{2})?)', proxy_desc)
        if value_match:
            try:
                value = Decimal(value_match.group(1).replace(',', ''))
            except:
                pass
        
        if not proxy_desc or proxy_desc == 'nan':
            return None
        
        return {
            'category': category or 'General',
            'subcategory': '',
            'proxy_name': proxy_desc[:200],
            'description': proxy_desc,
            'unit_of_measure': unit or 'per unit',
            'value': value or Decimal('0'),
            'geographic_scope': 'Surrey' if 'Surrey' in str(organisation) else 'Global',
            'data_year': 2024,
            'source_organisation': organisation or 'Surrey County Council',
        }
    
    def handle(self, *args, **options):
        pdf_path = 'SCC Proxies - Social Value Engine.pdf'
        
        self.stdout.write(f"Processing {pdf_path}...")
        
        imported = 0
        updated = 0
        current_category = "General"
        
        with pdfplumber.open(pdf_path) as pdf:
            self.stdout.write(f"Total pages: {len(pdf.pages)}")
            
            for i, page in enumerate(pdf.pages):
                if i < 5:  # Show progress for first 5 pages
                    self.stdout.write(f"Page {i+1}...")
                
                # Try table extraction
                tables = page.extract_tables()
                
                for table in tables:
                    for row in table:
                        proxy_data = self.parse_proxy_from_row(row, current_category)
                        
                        if proxy_data:
                            # Update current category if found
                            if proxy_data['category'] and proxy_data['category'] != 'General':
                                current_category = proxy_data['category']
                            
                            # Create or update
                            proxy, created = FinancialProxy.objects.update_or_create(
                                proxy_name=proxy_data['proxy_name'],
                                defaults={
                                    'category': proxy_data['category'],
                                    'subcategory': proxy_data['subcategory'],
                                    'description': proxy_data['description'],
                                    'unit_of_measure': proxy_data['unit_of_measure'],
                                    'value': proxy_data['value'],
                                    'currency': 'GBP',
                                    'geographic_scope': proxy_data['geographic_scope'],
                                    'data_year': proxy_data['data_year'],
                                    'source_organisation': proxy_data['source_organisation'],
                                    'outcome_name': proxy_data['proxy_name'],
                                    'financial_value_gbp': proxy_data['value'],
                                }
                            )
                            
                            # Link evidence
                            evidence = self.match_evidence(proxy_data['description'])
                            if evidence:
                                proxy.evidence_sources.set(evidence)
                            
                            if created:
                                imported += 1
                            else:
                                updated += 1
        
        self.stdout.write(self.style.SUCCESS(
            f"\nComplete! Imported {imported} new proxies, updated {updated} existing"
        ))
        self.stdout.write(f"Total in database: {FinancialProxy.objects.count()}")
