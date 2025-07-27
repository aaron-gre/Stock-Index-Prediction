import yfinance as yf
import pandas as pd
from datetime import datetime
import os

# --- Configuration ---
CONFIG = {
    "symbols": ["^GDAXI", "^MDAXI", "^SDAXI"],      # List of ticker symbols
    "symbol_names": {                              # Display names
        "^GDAXI": "DAX",
        "^MDAXI": "MDAX",
        "^SDAXI": "SDAX"
    },
    "start_date": "2022-06-01",                    # Start date (YYYY-MM-DD)
    "end_date": "2025-06-15",                      # End date (YYYY-MM-DD)
    "interval": "1d",                              # Interval: '1d', '1wk', '1mo'
    "output_dir": "01_Raw Data\yFinance API",                # Output directory
    "excel_filename": "stock_data.xlsx"            # Excel file name
}
# --------------------

class StockDataDownloader:
    """
    A class to download historical stock and ETF data from Yahoo Finance.
    
    This class provides functionality to:
    - Download historical data for multiple stocks/ETFs
    - Specify custom date ranges
    - Save data in Excel formats
    - Handle different time intervals (daily, weekly, monthly)
    """
    
    def __init__(self, output_dir, excel_filename, symbol_names=None):
        """
        Initialize the StockDataDownloader.
        
        Args:
            output_dir (str): Directory where downloaded files will be saved
            excel_filename (str): Name of the Excel file
            symbol_names (dict): Optional symbol name mapping
        """
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.output_dir = os.path.join(script_dir, output_dir)
        self.excel_filename = excel_filename
        self.symbol_names = symbol_names or {}
    
    def get_display_name(self, symbol):
        """Get display name for symbol, fallback to original symbol if not found"""
        return self.symbol_names.get(symbol, symbol)
    
    def download_data(self, symbols, start_date, end_date=None, interval='1d'):
        """
        Download historical data for the given symbols.
        
        Args:
            symbols (list): List of stock/ETF symbols (e.g., ['AAPL', '^GDAXI', '^IXIC'])
            start_date (str): Start date in 'YYYY-MM-DD' format
            end_date (str, optional): End date in 'YYYY-MM-DD' format. Defaults to today
            interval (str): Data interval ('1d' for daily, '1wk' for weekly, '1mo' for monthly)
            
        Returns:
            dict: Dictionary containing DataFrames for each symbol and their currency
        """
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
            
        data = {}
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                df = ticker.history(start=start_date, end=end_date, interval=interval)
                if not df.empty:
                    df.index = df.index.tz_localize(None)
                    info = ticker.info
                    currency = info.get('currency', 'EUR')
                    price_columns = ['Open', 'High', 'Low', 'Close']
                    for col in price_columns:
                        if col in df.columns:
                            df[col] = pd.to_numeric(df[col], errors='coerce').round(2)
                    data[symbol] = {'df': df, 'currency': currency}
                    display_name = self.get_display_name(symbol)
                    print(f"Successfully downloaded data for {display_name} ({currency})")
                else:
                    print(f"No data found for {symbol}")
            except Exception as e:
                print(f"Error downloading {symbol}: {str(e)}")
        
        return data
    
    def save_to_excel(self, data):
        """
        Save the downloaded data to an Excel file with multiple sheets.
        
        Args:
            data (dict): Dictionary containing DataFrames for each symbol
        """
        if not data:
            print("No data to save")
            return
            
        filename = os.path.join(self.output_dir, self.excel_filename)
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            for symbol, item in data.items():
                df = item['df'].copy()
                currency = item['currency']
                display_name = self.get_display_name(symbol)
                
                df.index = df.index.strftime('%d.%m.%Y')
                sheet_name = f"{display_name}_{currency}"
                df.to_excel(writer, sheet_name=sheet_name)
                
                worksheet = writer.sheets[sheet_name]
                
                price_columns = ['Open', 'High', 'Low', 'Close']
                for idx, col in enumerate(df.columns):
                    col_letter = chr(65 + idx + 1)  
                    if col in price_columns:
                        worksheet.column_dimensions[col_letter].number_format = '#,##0.00'
                    elif col == 'Volume':
                        worksheet.column_dimensions[col_letter].number_format = '#,##0'
                    try:
                        max_length = max(
                            df[col].astype(str).apply(len).max(),
                            len(str(col))
                        )
                        worksheet.column_dimensions[col_letter].width = max_length + 2
                    except:
                        worksheet.column_dimensions[col_letter].width = 12  
        
        print("Created stock_data.xlsx")


if __name__ == "__main__":
    # Create instance with values from CONFIG
    downloader = StockDataDownloader(
        output_dir=CONFIG["output_dir"],
        excel_filename=CONFIG["excel_filename"],
        symbol_names=CONFIG["symbol_names"]
    )
    
    data = downloader.download_data(
        symbols=CONFIG["symbols"],
        start_date=CONFIG["start_date"],
        end_date=CONFIG["end_date"],
        interval=CONFIG["interval"]
    )
    
    downloader.save_to_excel(data)
