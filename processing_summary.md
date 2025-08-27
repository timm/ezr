# Text Processing and TF-IDF with Information Gain Analysis

## Overview
Successfully processed raw text data from the moot text mining dataset using NLTK for preprocessing and calculated TF-IDF features with Information Gain for feature selection.

## Data Sources
- **Hall.csv**: 8,911 documents (8,912 rows including header)
- **Kitchenham.csv**: 1,704 documents (1,705 rows including header)  
- **Radjenovic.csv**: 6,000 documents (6,001 rows including header)
- **Wahono.csv**: 7,002 documents (7,003 rows including header)

## Preprocessing Pipeline
1. **Text Cleaning**: Removed special characters and normalized whitespace
2. **Tokenization**: Used NLTK's word_tokenize for word-level tokenization
3. **Stopword Removal**: Filtered out common English stopwords
4. **Stemming**: Applied Porter Stemmer to reduce words to root form
5. **Lemmatization**: Used WordNet Lemmatizer for proper word form reduction

## TF-IDF Configuration
- **Max Features**: 1,000 top features
- **N-gram Range**: (1, 2) - unigrams and bigrams
- **Min Document Frequency**: 2 (terms must appear in at least 2 documents)
- **Max Document Frequency**: 0.95 (terms appearing in >95% of documents are excluded)

## Information Gain Calculation
- Used mutual information between features and labels
- Sorted features by information gain in descending order
- Top 50 features with highest information gain were selected for final output

## Output Files Generated

### TF-IDF with Information Gain Files
- `Hall_tfidf_ig.csv` (3.1 MB) - 8,912 rows × 51 columns (label + 50 features)
- `Kitchenham_tfidf_ig.csv` (629 KB) - 1,705 rows × 51 columns
- `Radjenovic_tfidf_ig.csv` (2.2 MB) - 6,001 rows × 51 columns  
- `Wahono_tfidf_ig.csv` (2.7 MB) - 7,003 rows × 51 columns

### Feature Importance Files
- `Hall_feature_importance.csv` (29 KB) - 1,001 rows (feature names + information gain scores)
- `Kitchenham_feature_importance.csv` (29 KB) - 1,001 rows
- `Radjenovic_feature_importance.csv` (30 KB) - 1,001 rows
- `Wahono_feature_importance.csv` (29 KB) - 1,001 rows

## File Locations
All output files are saved in the same directory as the source data:
`../../GitHub/moot/text_mining/reading/raw/`

## Top Features by Information Gain (Sample from Hall dataset)
1. **softwar** (0.056) - Software-related terms
2. **predict** (0.051) - Prediction-related terms
3. **use** (0.047) - Usage-related terms
4. **model** (0.041) - Model-related terms
5. **data** (0.038) - Data-related terms
6. **paper** (0.038) - Paper/document-related terms
7. **fault** (0.035) - Fault-related terms
8. **result** (0.034) - Result-related terms
9. **base** (0.033) - Base-related terms

## Technical Implementation
- **Script**: `ezr/tfidf_ig.py`
- **Dependencies**: NLTK, pandas, scikit-learn
- **Processing Time**: ~39 seconds for all datasets
- **Memory Usage**: Efficient sparse matrix representation for large datasets

## File Structure
Each output file contains:
- **TF-IDF files**: Label column + 100 TF-IDF feature columns (top features by information gain)
- **Feature importance files**: Feature names and their corresponding information gain scores

The processed data is now ready for machine learning applications, with features ranked by their discriminative power for the classification task.
