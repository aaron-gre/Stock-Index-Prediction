from pypdf import PdfReader
import os
import re
import glob
import pandas as pd
from datetime import datetime

# Configuration - adjust only these entries
CONFIG = {
    # Input folder with the ECB PDFs
    "pdf_folders": {
        "ECB": "01_Raw Data\ECB PDF Downloads"
    },
    # Output folder where the extracted text files are written
    "text_output": "02_Preprocessing\TEXT",
    # Excel generation settings
    "input_folder": "02_Preprocessing\TEXT\ECB",       # folder with ECB sub-folders
    "output_folder": "02_Preprocessing",               # folder where Excel file will be saved
    "excel_filename": "ECB Press Release Days.xlsx"    # output file
}

# .py file must be in the same folder as the PDF folders
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

def get_date_format_choice():
    """Ask user to choose date format"""
    print("\nChoose Date Format:")
    print("1 - Month as text (e.g., 17_April_2025)")
    print("2 - Month as number (e.g., 17_04_2025)")

    while True:
        choice = input("\nEnter your choice (1 or 2): ").strip()
        if choice == "1":
            return "text"
        elif choice == "2":
            return "number"
        else:
            print("Invalid choice. Please enter 1 or 2.")

def convert_month_to_number(month_name):
    """Convert month name to number with leading zero"""
    month_mapping = {
        'january': '01', 'jan': '01',
        'february': '02', 'feb': '02',
        'march': '03', 'mar': '03',
        'april': '04', 'apr': '04',
        'may': '05',
        'june': '06', 'jun': '06',
        'july': '07', 'jul': '07',
        'august': '08', 'aug': '08',
        'september': '09', 'sep': '09',
        'october': '10', 'oct': '10',
        'november': '11', 'nov': '11',
        'december': '12', 'dec': '12'
    }
    return month_mapping.get(month_name.lower(), month_name)

def extract_date_from_filename(pdf_name, date_format):
    """
    Extract date from PDF filename for PRESS CONFERENCE files
    Expected format: "PRESS CONFERENCE_6_March_2025.pdf"
    """
    basename = os.path.splitext(os.path.basename(pdf_name))[0]

    if basename.startswith("PRESS CONFERENCE_"):
        date_part = basename[len("PRESS CONFERENCE_"):]
        parts = date_part.split('_')
        if len(parts) == 3:
            day, month_name, year = parts
            day = day.zfill(2)

            if date_format == "number":
                month_number = convert_month_to_number(month_name)
                formatted_date = f"{day}_{month_number}_{year}"
            else:
                formatted_date = f"{day}_{month_name}_{year}"
            
            return formatted_date
    
    return None

def extract_date_from_text(text, date_format, pdf_name):
    """
    Extracts the date that appears after "Combined monetary policy decisions and statement"
    If no date found in text and PDF is PRESS CONFERENCE, extract from filename
    """
    pattern = r'Combined monetary policy decisions and\s*statement\s*(\d{1,2}\s+\w+\s+\d{4})'
    
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        date_str = match.group(1).strip()
        
        date_parts = date_str.split()
        if len(date_parts) == 3:
            day = date_parts[0].zfill(2)
            month_name = date_parts[1]
            year = date_parts[2]
            
            if date_format == "number":
                month_number = convert_month_to_number(month_name)
                formatted_date = f"{day}_{month_number}_{year}"
            else:
                formatted_date = f"{day}_{month_name}_{year}"
            
            return formatted_date
        else:
            formatted_date = date_str.replace(" ", "_")
            return formatted_date
    
    basename = os.path.basename(pdf_name)
    if basename.startswith("PRESS CONFERENCE"):
        filename_date = extract_date_from_filename(pdf_name, date_format)
        if filename_date:
            return filename_date
    
    pdf_basename = os.path.splitext(os.path.basename(pdf_name))[0]
    fallback_name = f"xxxx_no date found__{pdf_basename}"
    return fallback_name

def get_unique_folder_name(base_path, folder_name):
    """
    Creates a unique folder name by adding 'new' if folder already exists
    """
    original_path = os.path.join(base_path, folder_name)
    
    if not os.path.exists(original_path):
        return folder_name
    
    current_name = folder_name
    while True:
        new_folder_name = f"{current_name}new"
        new_path = os.path.join(base_path, new_folder_name)
        if not os.path.exists(new_path):
            return new_folder_name
        current_name = new_folder_name

def extract_sections_precise(text, headers):
    """
    Extracts sections only when headers appear alone on a line
    Special handling for Conclusion section which ends at "We are now ready to take your questions."
    """
    lines = text.splitlines()
    sections = {}
    current_section = None
    current_text = []

    for line in lines:
        stripped_line = line.strip()
        
        if current_section and current_section.lower() == "conclusion":
            if "we are now ready to take your questions" in stripped_line.lower():
                current_text.append(line)
                sections[current_section] = '\n'.join(current_text).strip()
                current_section = None
                current_text = []
                continue
        
        if any(stripped_line.lower() == h.lower() for h in headers):
            if current_section:
                sections[current_section] = '\n'.join(current_text).strip()
            
            current_section = stripped_line
            current_text = [stripped_line]
        else:
            if current_section:
                current_text.append(line)

    if current_section:
        sections[current_section] = '\n'.join(current_text).strip()

    return sections

def process_single_pdf(pdf_file, central_bank, date_format):
    """
    Process a single PDF file
    """
    try:
        reader = PdfReader(pdf_file)
        text = ""

        for page in reader.pages:
            text += page.extract_text()

        extracted_date = extract_date_from_text(text, date_format, pdf_file)
        
        base_path = os.path.join(CONFIG["text_output"], central_bank)
        unique_folder_name = get_unique_folder_name(base_path, extracted_date)
        
        date_folder = os.path.join(base_path, unique_folder_name)
        os.makedirs(date_folder, exist_ok=True)
        
        txt_file = os.path.join(date_folder, "0_FULL.txt")
        with open(txt_file, "w", encoding="utf-8") as f:
            f.write(text)

        headers = [
            "Financial and monetary conditions",
            "Inflation", 
            "Economic activity",
            "Risk assessment",
            "Press conference",
            "Conclusion"
        ]
        
        sections = extract_sections_precise(text, headers)
        
        section_mapping = {
            "Conclusion": "1_CONCLUSION",
            "Inflation": "2_INFLATION",
            "Economic activity": "3_ECONOMIC_ACTIVITY",
            "Risk assessment": "4_RISK_ASSESSMENT",
            "Press conference": "5_PRESS_CONFERENCE",
            "Financial and monetary conditions": "6_FINANCIAL_MONETARY_CONDITIONS"
        }
        
        for section_title, section_content in sections.items():
            if section_title in section_mapping:
                section_key = section_mapping[section_title]
                section_filename = f"{section_key}.txt"
                section_file = os.path.join(date_folder, section_filename)
                
                with open(section_file, "w", encoding="utf-8") as f:
                    f.write(section_content)

        return True
        
    except Exception as e:
        return False

def list_and_process_folders():
    """
    Generate Excel file with folder dates after PDF processing is complete
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_path = os.path.join(script_dir, CONFIG["input_folder"])

    # all sub-folders inside the ECB directory
    folders = sorted(
        d for d in os.listdir(target_path)
        if os.path.isdir(os.path.join(target_path, d))
    )

    # extract dates from folder names of form 17_April_2025
    def parse_folder(name: str):
        day, month_name, year = name.split('_')
        date_obj = datetime.strptime(f"{day} {month_name} {year}", "%d %B %Y")
        return {
            "folder_name": name,
            "date": date_obj.strftime("%d.%m.%Y"),
            "datetime": date_obj
        }

    data = [parse_folder(f) for f in folders]

    df = (pd.DataFrame(data)
            .sort_values("datetime")
            .reset_index(drop=True))

    # save Excel file (only folder_name and date columns)
    output_path = os.path.join(script_dir, CONFIG["output_folder"])
    df[["folder_name", "date"]].to_excel(
        os.path.join(output_path, CONFIG["excel_filename"]),
        index=False
    )
    return df

# Main batch processing
try:
    central_bank = "ECB"
    date_format = get_date_format_choice()
    
    pdf_folder = CONFIG["pdf_folders"][central_bank]
    pdf_files = glob.glob(os.path.join(pdf_folder, "*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in folder: {pdf_folder}")
        exit()
    
    successful = 0
    failed = 0
    
    for pdf_file in pdf_files:
        if process_single_pdf(pdf_file, central_bank, date_format):
            successful += 1
        else:
            failed += 1
    
    print(f"Date Format: {'Month as text' if date_format == 'text' else 'Month as number'}")
    print(f"Successfully processed: {successful} PDFs")
    print(f"Failed: {failed} PDFs")
    print(f"Total: {len(pdf_files)} PDFs")
    print(f"All files saved to: {CONFIG['text_output']}/{central_bank}/")
    
    print(f"\nGenerating Excel file...")
    list_and_process_folders()
    print(f"Excel file created: {CONFIG['excel_filename']}")
    
except Exception as e:
    print(f"Critical error during batch processing: {e}")
