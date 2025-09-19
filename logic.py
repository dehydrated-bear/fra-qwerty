import pdfplumber
import json
import re
from conversion import kru2uni  # Tumhara Kruti → Unicode converter

pdf_path = "in.pdf"

columns = [
    "Letter_No_Date",
    "Holder_Name", 
    "Father_Mother_Name",
    "Address",
    "Caste_Status",
    "Purpose",
    "Dependents_Names",
    "Dependents_Relationship",
    "Village_Details",
    "Khasra_No",
    "Land_Area",
    "Forest_Block_Name",
    "Compartment_No",
    "GPS_Address",
    "Special_Remarks",
    "Officer_Signature",
    "Checker_Signature"
]

all_data = []

# -------------------------------
# Helpers
# -------------------------------
def is_header_row(record):
    text = " ".join(record).strip()
    header_keywords = ["वन मण्डल", "रेंज", "गांव", "जिला स्तरीय", "एकल धारक"]
    return any(kw in text for kw in header_keywords)

def is_number_header(record):
    return all(cell.strip().isdigit() for cell in record if cell.strip())

def is_empty_row(record):
    return all(cell.strip() == "" for cell in record)

def convert_bigha_to_hectare(text):
    """Convert multi-line 'बीघा' values into hectares and remove 'बीघा' word (including spaced versions)"""
    if not text:
        return text
    
    # Check for both "बीघा" and spaced variations like "बी घा"
    has_bigha = "बीघा" in text or "बी घा" in text or "बीघ" in text

    if not has_bigha:
        return text

    converted_lines = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue

        # Remove all variations of बीघा (including spaced ones)
        line_without_bigha = line
        bigha_variations = ["बीघा", "बी घा", "बीघ", "घा"]
        for variation in bigha_variations:
            line_without_bigha = line_without_bigha.replace(variation, "")
        
        line_without_bigha = line_without_bigha.strip()
        
        # Extract all numbers (including decimal numbers) from the line
        numbers = re.findall(r"\d+(?:\.\d+)?", line_without_bigha)
        
        if numbers:
            converted_nums = []
            for num_str in numbers:
                try:
                    val = float(num_str)
                    hectare = val * 0.25  # 1 बीघा = 0.25 hectare
                    # Format to remove unnecessary decimal places
                    if hectare == int(hectare):
                        converted_nums.append(str(int(hectare)))
                    else:
                        converted_nums.append(f"{hectare:.3f}".rstrip('0').rstrip('.'))
                except ValueError:
                    converted_nums.append(num_str)
            
            # For simple cases with just numbers, join with spaces
            if len(converted_nums) > 0:
                converted_lines.append(" ".join(converted_nums))
        else:
            # No numbers found, keep the line as is (without बीघा variations)
            if line_without_bigha:
                converted_lines.append(line_without_bigha)

    return "\n".join(converted_lines)

# -------------------------------
# Main Loop  
# -------------------------------
with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        tables = page.extract_tables()
        if not tables:
            continue

        for table in tables:
            for row in table:
                if not row:
                    continue

                row_data = [kru2uni(cell) if cell else "" for cell in row[1:]]

                # Replace "ध्" → "/" in Letter_No_Date
                if row_data and row_data[0]:
                    row_data[0] = row_data[0].replace("ध्", "/")

                # Replace "ण्" and "ण" → "."
                row_data = [
                    cell.replace("ण्", ".").replace("ण", ".") if cell else ""
                    for cell in row_data
                ]

                # Convert बीघा → hectare in Land_Area
                if len(row_data) > 10 and row_data[10]:  # Land_Area is at index 10
                    row_data[10] = convert_bigha_to_hectare(row_data[10])

                if is_header_row(row_data) or is_number_header(row_data) or is_empty_row(row_data):
                    continue

                record = dict(zip(columns, row_data))
                all_data.append(record)

# -------------------------------
# Save Clean JSON
# -------------------------------
with open("fra_records.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

print("✅ Cleaned data saved into fra_records.json")
