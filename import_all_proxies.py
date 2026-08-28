import csv
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sv_platform.settings')
django.setup()
from decimal import Decimal
from sv_platform.apps.impact.models import FinancialProxy

def parse_value(value_str):
    if not value_str:
        return Decimal('0')
    value_str = str(value_str).replace('£', '').replace(',', '').strip()
    if '-' in value_str:
        parts = value_str.split('-')
        try:
            return (Decimal(parts[0]) + Decimal(parts[1])) / 2
        except:
            return Decimal('0')
    try:
        return Decimal(value_str)
    except:
        return Decimal('0')

def import_csv_file(filepath, framework):
    imported = 0
    updated = 0
    print(f"\nImporting {framework} from {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get('Proxy') and not row.get('Category'):
                continue
            value = parse_value(row.get('£ Value', ''))
            proxy_data = {
                'category': row.get('Category', 'General')[:100],
                'subcategory': '',
                'proxy_name': row.get('Proxy', '')[:200],
                'description': row.get('Proxy', ''),
                'unit_of_measure': row.get('Unit', '')[:100],
                'value': value,
                'currency': 'GBP',
                'financial_value_gbp': value,
                'geographic_scope': 'Surrey' if framework == 'SCC' else 'Global',
                'data_year': 2024,
                'source_organisation': 'Surrey County Council' if framework == 'SCC' else 'Various',
                'evidence_url': row.get('Evidence', '')[:500],
                'evidence_match': row.get('Evidence Match', '')[:100],
                'evidence_note': row.get('Evidence Note', ''),
                'research_batch': row.get('Research Batch', '')[:50],
                'framework': framework,
            }
            proxy, created = FinancialProxy.objects.update_or_create(
                proxy_name=proxy_data['proxy_name'],
                framework=framework,
                defaults=proxy_data
            )
            if created:
                imported += 1
            else:
                updated += 1
            if (imported + updated) % 50 == 0:
                print(f"  Processed {imported + updated}...")
    print(f"  Complete: {imported} imported, {updated} updated")
    return imported, updated

if __name__ == '__main__':
    total_imported = 0
    total_updated = 0
    if os.path.exists('Consolidated SCC Proxies-Table 1.csv'):
        i, u = import_csv_file('Consolidated SCC Proxies-Table 1.csv', 'SCC')
        total_imported += i
        total_updated += u
    if os.path.exists('All Global Proxies-Table 1.csv'):
        i, u = import_csv_file('All Global Proxies-Table 1.csv', 'GLOBAL')
        total_imported += i
        total_updated += u
    print(f"\n{'='*60}")
    print(f"TOTAL IMPORTED: {total_imported}")
    print(f"TOTAL UPDATED: {total_updated}")
    print(f"TOTAL IN DATABASE: {FinancialProxy.objects.count()}")
    print(f"{'='*60}")
