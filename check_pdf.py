import pdfplumber

with pdfplumber.open('SCC Proxies - Social Value Engine.pdf') as pdf:
    print(f"Total pages: {len(pdf.pages)}")
    
    # Show first 3 pages
    for i in range(min(3, len(pdf.pages))):
        print(f"\n{'='*50}")
        print(f"PAGE {i+1}")
        print('='*50)
        text = pdf.pages[i].extract_text()
        print(text[:1000])  # First 1000 characters
        print("\n...")
