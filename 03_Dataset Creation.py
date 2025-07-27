import pandas as pd
import os
import numpy as np

# Configuration - adjust only these entries
CONFIG = {
    "input_folder_interest": "02_Preprocessing\Interest_Rate_Preprocessed",
    "interest_file": "interest_rate_2022_2025.xlsx",
    "input_folder_stock": "02_Preprocessing\Stock_Preprocessed",
    "stock_file": "stock_data_combined_onehot.xlsx",
    "input_folder_sentiment": "02_Preprocessing\KAGGLE_Sentiment-Analysis",
    "sentiment_file": "ecb_sentiment_analysis.xlsx",
    "output_folder": "03_Dataset Creation\Datasets",
    "excel_filename": "DS_14_t_3days_complete.xlsx",
    "remove_dates": ['2024-12-12', '2022-06-09']  # Outliers to remove
}

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Load and prepare data
df_interest = pd.read_excel(f"{CONFIG['input_folder_interest']}/{CONFIG['interest_file']}", index_col=0, parse_dates=True)
df_stock = pd.read_excel(f"{CONFIG['input_folder_stock']}/{CONFIG['stock_file']}", index_col=0, parse_dates=True)

# Convert data formats
onehot_cols = [col for col in df_stock.columns if col.startswith('Index_')]
df_stock[onehot_cols] = df_stock[onehot_cols].astype(float)
for df in [df_stock, df_interest]:
    df.index = pd.to_datetime(df.index, format='%d.%m.%Y')

# Create base dataset
common_dates = df_stock.index.intersection(df_interest.index)
df_neu = df_stock.loc[common_dates].copy()

# Initialize historical and future price columns
for i in range(1, 15):
    df_neu.insert(i-1, f'Close_t-{15-i}', np.nan)
for i in range(1, 4):
    df_neu.insert(15 + i, f'Close_t+{i}', np.nan)

# Fill price data
index_columns = ['Index_DAX', 'Index_MDAX', 'Index_SDAX']
for i in range(len(df_neu)):
    row = df_neu.iloc[i]
    column_with_one = [col for col in index_columns if row[col] == 1.0][0]
    mask = (df_stock.index == df_neu.index[i]) & (df_stock[column_with_one] == 1.0)
    
    if mask.any():
        iloc_position = np.where(mask)[0][0]
        try:
            for j in range(14, 0, -1):
                df_neu.iloc[i, df_neu.columns.get_loc(f'Close_t-{j}')] = df_stock.iloc[iloc_position - j]['Close']
            for j in range(1, 4):
                df_neu.iloc[i, df_neu.columns.get_loc(f'Close_t+{j}')] = df_stock.iloc[iloc_position + j]['Close']
        except IndexError:
            pass

# Add interest rate and sentiment data
df_neu['Interest Rate_Old'] = df_interest.loc[common_dates, 'Interest Rate_Old']
df_neu['Interest Rate_Change'] = df_interest.loc[common_dates, 'Interest Rate_Change']

df_sentiment = pd.read_excel(f"{CONFIG['input_folder_sentiment']}/{CONFIG['sentiment_file']}").iloc[:-1]
df_sentiment['Date'] = pd.to_datetime(df_sentiment['Date'], format='%d_%B_%Y')
df_sentiment.set_index('Date', inplace=True)

sentiment_columns = ['FinBERT_Sentences', 'FinBERT_Chunks', 'RoBERTa_Sentences', 'RoBERTa_Chunks']
for col in sentiment_columns:
    df_neu[col] = df_neu.index.map(df_sentiment[col])

# Save complete dataset
os.makedirs(CONFIG['output_folder'], exist_ok=True)
df_neu.to_excel(f"{CONFIG['output_folder']}/{CONFIG['excel_filename']}", index=True)

print("df_neu (final dataset):")
print(df_neu)
print(f"\ndf_neu dimensions: {df_neu.shape[0]} rows × {df_neu.shape[1]} columns")

# ===== ADDITIONAL PROCESSING: Create different dataset variants =====

# Remove outliers
remove_dates = pd.to_datetime(CONFIG['remove_dates'])
df_filtered = df_neu.loc[~df_neu.index.isin(remove_dates)]

# Define feature groups
price_columns = ['Close_t-4', 'Close_t-3', 'Close_t-2']
feature_columns_with_old = ['Index_MDAX', 'Index_SDAX', 'Interest Rate_Old', 'Interest Rate_Change']
base_columns = price_columns + feature_columns_with_old
target_columns = ['Close', 'Close_t+1', 'Close_t+2']

# Create percentage-based targets
df_targets = df_filtered.copy()
for col in target_columns:
    df_targets[col] = (df_filtered[col] - df_filtered['Close_t-1']) / df_filtered['Close_t-1'] * 100

# Create percentage-based features
df_features = df_filtered[base_columns + sentiment_columns].copy()
for col in price_columns:
    df_features[col] = (df_filtered[col] - df_filtered['Close_t-1']) / df_filtered['Close_t-1'] * 100

# Create different dataset variants
datasets = {}

# 1. Complete Dataset (all features)
df_complete = df_features[base_columns + sentiment_columns].copy()
for col in target_columns:
    df_complete[col] = df_targets[col]
datasets['dataset'] = df_complete

# 2. Base Dataset (no sentiment)
df_base = df_features[base_columns].copy()
for col in target_columns:
    df_base[col] = df_targets[col]
datasets['dataset_base'] = df_base

# 3. Individual sentiment datasets
sentiment_variants = {
    'dataset_finbert_sentences': ['FinBERT_Sentences'],
    'dataset_finbert_chunks': ['FinBERT_Chunks'],
    'dataset_roberta_sentences': ['RoBERTa_Sentences'],
    'dataset_roberta_chunks': ['RoBERTa_Chunks']
}

for name, sentiment_cols in sentiment_variants.items():
    df_temp = df_features[base_columns + sentiment_cols].copy()
    for col in target_columns:
        df_temp[col] = df_targets[col]
    datasets[name] = df_temp

# Export all datasets
print("\nExporting dataset variants...")
for name, df in datasets.items():
    df.to_excel(f"{CONFIG['output_folder']}/{name}.xlsx")

print("All datasets exported successfully!")
for name, df in datasets.items():
    print(f"{name} Shape: {df.shape}")
