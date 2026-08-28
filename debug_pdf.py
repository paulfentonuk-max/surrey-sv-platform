import pdfplumber

with pdfplumber.open('SCC Proxies - Social Value Engine.pdf') as pdf:
    for i in range(3):  # First 3 pages
        print(f"\n{'='*60}")
        print(f"PAGE {i+1}")
        print('='*60)
        
        page = pdf.pages[i]
        
        # Try to extract tables
        tables = page.extract_tables()
        print(f"\nFound {len(tables)} tables")
        
        for t_idx, table in enumerate(tables):
            print(f"\nTable {t_idx+1} ({len(table)} rows):")
            for row_idx, row in enumerate(table[:5]):  # First 5 rows
                print(f"  Row {row_idx}: {row}")
