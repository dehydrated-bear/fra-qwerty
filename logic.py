import pdfplumber
from conversion import kru2uni  # Your Kruti → Unicode function

pdf_path = "in.pdf"

with pdfplumber.open(pdf_path) as pdf:
    lol = [pdf.pages[0], pdf.pages[1]]
    for i, page in enumerate(lol):
        print(f"--- Page {i+1} ---")
        
        # Extract tables first
        tables = page.extract_tables()
        if tables:
            for table_index, table in enumerate(tables, start=1):
                print(f"\nTable {table_index}:")
                for row in table:
                    # Convert each cell from Kruti Dev to Unicode
                    converted_row = [kru2uni(cell) if cell else "" for cell in row]
                    print(converted_row)
        else:
            # Fallback: extract raw text
            raw_text = page.extract_text()
            if raw_text:
                unicode_text = kru2uni(raw_text)
                print(unicode_text)
            else:
                print("No extractable content found on this page.")
