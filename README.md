## Project Overview

This project investigates whether interest rate change announcements by the European Central Bank (ECB) create predictable movements in German stock market indices. The study combines financial data with sentiment analysis of ECB press conference transcripts, using machine learning models (baseline, linear regression, polynomial regression) to forecast short-term stock price changes. Sentiment scores are generated from full press conference texts using a fine-tuned financial language model (FinBERT) and combined with financial features. Model performance is evaluated using mean squared error (MSE) and the coefficient of determination (R²) on a custom dataset covering multiple ECB announcement cycles. The project highlights both the potential and limitations of integrating sentiment analysis with financial features for market prediction.

## Prerequisites / Dependencies

- Python 3.8 or higher
- Required Python packages:
    pandas, numpy, scikit-learn, yfinance, transformers, nltk, pypdf, matplotlib
- (Optional) Kaggle account for running Kaggle notebooks and using uploaded datasets







# How the Data was gathered/processed

## Step 1: Collecting Data

- **Financial Data (API):**  
  Start `01_stock_data_downloader.py`
   -> Creates  'stock_data.xlsx' in folder [01_Raw Data/yFinance API](01_Raw%20Data/yFinance%20API)

- **ECB Data (from Browser):**  
  PDFs downloaded from [ECB Press Releases](https://www.ecb.europa.eu/press/govcdec/mopo/html/index.en.html) to folder [01_Raw Data/ECB PDF Downloads](01_Raw%20Data/ECB%20PDF%20Downloads)  
  Interest Rate and Change from [ECB Interest Rate Data](https://data.ecb.europa.eu/data/datasets/FM/FM.B.U2.EUR.4F.KR.DFR.LEV) to folder [01_Raw Data/ECB Download](01_Raw%20Data/ECB%20Download)

---

## Step 2: Preprocessing

- PDF to .txt extraction: Start `02_pdf to txt transformer_bulk.py`.  
  -> creates date folders with .txt files in [02_Preprocessing/TEXT/ECB](02_Preprocessing/TEXT/ECB)  
  -> creates `EZB Press Release Days.xlsx` in [02_Preprocessing](02_Preprocessing)

- PDF to .txt extraction: Start `02_pdf to txt transformer_bulk.py`.
    -> creates date folders with .txt files in [02_Preprocessing/TEXT/ECB](02_Preprocessing/TEXT/ECB)
    -> creates `EZB Press Release Days.xlsx` in [02_Preprocessing](02_Preprocessing)

- Combining Interest Rate .xlsx's: Start `02_excel interestrate parser.py`.
    -> creates `interest_rate_2022_2025.xlsx` in [02_Preprocessing/Interest_Rate_Preprocessed](02_Preprocessing/Interest_Rate_Preprocessed)

- Combining and One Hot Encoding Stockdata: Start `02_stock_data_one_hot.py`.
    -> creates `stock_data_combined_onehot.xlsx` in [02_Preprocessing/Stock_Preprocessed](02_Preprocessing/Stock_Preprocessed)


---

## Step 2.1: Sentiment Analysis

- Extract Sentiment Analysis:
  - Load `02-1-Sentiment-Analysis.ipynb` from [02_Preprocessing/KAGGLE_Sentiment-Analysis](02_Preprocessing/KAGGLE_Sentiment-Analysis) into Kaggle  
  - Integrate Dataset: [llm-text](https://kaggle.com/datasets/7c259f2a2bfe3bc39138ff3856969397cd09f498515434bb2459e8b512711e2c)  
  - Or just click the link and it's preloaded: [Sentiment Analysis Notebook](https://www.kaggle.com/code/aarongresser/02-1-sentiment-analysis)  
  - Run code below the markdown "All Models Compared"  
  - Downloaded `ecb_sentiment_analysis.xlsx` into the folder [02_Preprocessing/KAGGLE_Sentiment-Analysis](02_Preprocessing/KAGGLE_Sentiment-Analysis)

---

## Step 3: Dataset Creation

- Create complete datasets:
  - Start `03_Dataset Creation.py`   
     -> creates multiple `.xlsx` in [Dataset](03_Dataset%20Creation/Datasets)  
  - Uploaded it to Kaggle: ["Datasets_NaiveBayes.zip"](https://kaggle.com/datasets/8b0f9663f57b56f070d7635f52d0f2629b0aa6f3a9678d3454d8355580490204)
 
## Step 3.1: Dataset Visualisation

- Load `03-dataset-visualization.ipynb` from [03_Dataset Creation](03_Dataset%20Creation) into Kaggle    
 - Load the dataset: [Datasets_NaiveBayes](https://kaggle.com/datasets/8b0f9663f57b56f070d7635f52d0f2629b0aa6f3a9678d3454d8355580490204)  
 - Or just click the link and it's preloaded: [Dataset Visualization Notebook](https://www.kaggle.com/code/aarongresser/03-dataset-visualization)
 - Complete run


---

# Model Training

### Step 4: Hyperparameter Configuration

- Load `04-hyperparamter-configuration.ipynb` from [04_Hyperparamter Tuning](04_Hyperparamter%20Tuning) into Kaggle  
- Load the dataset: [Datasets_NaiveBayes](https://kaggle.com/datasets/8b0f9663f57b56f070d7635f52d0f2629b0aa6f3a9678d3454d8355580490204)  
- Or just click the link and it's preloaded: [Hyperparameter Config Notebook](https://www.kaggle.com/code/aarongresser/04-hyperparamter-configuration)  
- Complete run

### Step 5: Model Training

- Load `05-modell-training.ipynb` from [05_Modell Training](05_Modell%20Training) into Kaggle  
- Load the dataset: [Datasets_NaiveBayes](https://kaggle.com/datasets/8b0f9663f57b56f070d7635f52d0f2629b0aa6f3a9678d3454d8355580490204)
- Or just click the link and it's preloaded: [Model Training Notebook](https://www.kaggle.com/code/aarongresser/05-modell-training)  
- Complete run


## Author

Aaron Gresser 

The Paper to this code can be found [here](Data%20Science%20in%20Practice.pdf)
