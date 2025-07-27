import pandas as pd
import os
from datetime import datetime
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

# Configuration - adjust only these entries
CONFIG = {
    "input_folder": "01_Raw Data\ECB Download",
    "change_file": "2022_2025_change.xlsx",
    "rate_file": "2022_2025_rate.xlsx",
    "input_folder_date": "02_Preprocessing",
    "date_file": "ECB Press Release Days.xlsx",
    "output_folder": "02_Preprocessing\Interest_Rate_Preprocessed",
    "excel_filename": "interest_rate_2022_2025.xlsx"
}

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Load and clean both ECB files
ecb_files = {}
for file_key in ['rate_file', 'change_file']:
    df = (pd.read_excel(f"{CONFIG['input_folder']}/{CONFIG[file_key]}")
          .iloc[13:].reset_index(drop=True))
    df.columns = df.iloc[0]
    df = df.drop(df.index[0]).reset_index(drop=True)
    
    df = df.rename(columns={
        "Deposit facility - date of changes (raw data) - Level (FM.D.U2.EUR.4F.KR.DFR.LEV)": "Interest Rate",
        "Deposit facility - date of changes (raw data) - Level (FM.D.U2.EUR.4F.KR.DFR.LEV) - Modified value (Period-to-period change)": "Interest Rate_Change"
    })
    
    df['DATE'] = pd.to_datetime(df['DATE'])
    ecb_files[file_key] = df[df['DATE'] > datetime(2022, 5, 31)].reset_index(drop=True)

# Merge and clean ECB data
df_combined = pd.merge(ecb_files['rate_file'], 
                      ecb_files['change_file'][['DATE', 'Interest Rate_Change']], 
                      on='DATE', how='left').drop('TIME PERIOD', axis=1)

# Convert to numeric and prepare for date merge
for col in ['Interest Rate', 'Interest Rate_Change']:
    df_combined[col] = pd.to_numeric(df_combined[col], errors='coerce')

# Load dates and merge with press release dates
df_date = pd.read_excel(f"{CONFIG['input_folder_date']}/{CONFIG['date_file']}").drop(columns=['folder_name'], errors='ignore')
df_combined = df_combined.rename(columns={'DATE': 'date'})

for df in [df_combined, df_date]:
    df['date'] = pd.to_datetime(df['date'], format='%d.%m.%Y')

# Final merge and processing
df_final = (pd.merge(df_combined, df_date, on='date', how='inner')
           .sort_values('date').reset_index(drop=True))

df_final['Interest Rate_Change'] = df_final['Interest Rate'].diff().fillna(0)
df_final = df_final.rename(columns={'Interest Rate': 'Interest Rate_Old', 'date': 'Date'})
df_final['Date'] = df_final['Date'].dt.strftime('%d.%m.%Y')

# Save and display
os.makedirs(CONFIG['output_folder'], exist_ok=True)
df_final.to_excel(f"{CONFIG['output_folder']}/{CONFIG['excel_filename']}", index=False)

print(f"Dimensions: {df_final.shape[0]} rows × {df_final.shape[1]} columns")

print(df_final.head(5))

print("\nColumn data types:")
for col in df_final.columns:
    print(f"   • {col}: {df_final[col].dtype}")

print(f"\n File saved: {CONFIG['output_folder']}/{CONFIG['excel_filename']}")
