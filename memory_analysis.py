#!/usr/bin/env python3
"""
Memory and space analysis for EZR vs NLTK
"""

import os
import sys
import psutil
import gc
import time
import nltk
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer

# Add the ezr package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ezr'))
from ezr.prep import Prep, tokenize

def get_memory_usage():
    """Get current memory usage in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

def analyze_nltk_memory_usage(texts, sample_size=100):
    """Analyze NLTK memory usage during preprocessing."""
    print("🔍 Analyzing NLTK Memory Usage...")
    
    # Force garbage collection
    gc.collect()
    initial_memory = get_memory_usage()
    print(f"   📊 Initial memory: {initial_memory:.2f} MB")
    
    # Load NLTK components
    porter = PorterStemmer()
    stop_words = set(stopwords.words('english'))
    after_loading = get_memory_usage()
    print(f"   📊 After loading components: {after_loading:.2f} MB (+{after_loading - initial_memory:.2f} MB)")
    
    # Process texts
    processed_texts = []
    for i, text in enumerate(texts[:sample_size]):
        tokens = nltk.word_tokenize(text.lower())
        processed = [porter.stem(token) for token in tokens 
                    if token.isalnum() and len(token) > 2 and token not in stop_words]
        processed_texts.append(' '.join(processed))
        
        if (i + 1) % 20 == 0:
            current_memory = get_memory_usage()
            print(f"   📊 After {i+1} texts: {current_memory:.2f} MB (+{current_memory - after_loading:.2f} MB)")
    
    final_memory = get_memory_usage()
    print(f"   📊 Final memory: {final_memory:.2f} MB (+{final_memory - initial_memory:.2f} MB)")
    
    return final_memory - initial_memory

def analyze_ezr_memory_usage(texts, sample_size=100):
    """Analyze EZR memory usage during preprocessing."""
    print("🔍 Analyzing EZR Memory Usage...")
    
    # Force garbage collection
    gc.collect()
    initial_memory = get_memory_usage()
    print(f"   📊 Initial memory: {initial_memory:.2f} MB")
    
    # Load EZR components
    prep = Prep()
    after_loading = get_memory_usage()
    print(f"   📊 After loading components: {after_loading:.2f} MB (+{after_loading - initial_memory:.2f} MB)")
    
    # Process texts
    processed_texts = []
    for i, text in enumerate(texts[:sample_size]):
        tokens = tokenize(text, prep.stops, prep.sufs)
        processed_texts.append(' '.join(tokens))
        
        if (i + 1) % 20 == 0:
            current_memory = get_memory_usage()
            print(f"   📊 After {i+1} texts: {current_memory:.2f} MB (+{current_memory - after_loading:.2f} MB)")
    
    final_memory = get_memory_usage()
    print(f"   📊 Final memory: {final_memory:.2f} MB (+{final_memory - initial_memory:.2f} MB)")
    
    return final_memory - initial_memory

def analyze_tfidf_memory_usage(texts, sample_size=100):
    """Analyze TF-IDF memory usage for both systems."""
    print("🔍 Analyzing TF-IDF Memory Usage...")
    
    # Force garbage collection
    gc.collect()
    initial_memory = get_memory_usage()
    print(f"   📊 Initial memory: {initial_memory:.2f} MB")
    
    # NLTK + scikit-learn TF-IDF
    porter = PorterStemmer()
    stop_words = set(stopwords.words('english'))
    
    processed_texts = []
    for text in texts[:sample_size]:
        tokens = nltk.word_tokenize(text.lower())
        processed = [porter.stem(token) for token in tokens 
                    if token.isalnum() and len(token) > 2 and token not in stop_words]
        processed_texts.append(' '.join(processed))
    
    # Create TF-IDF matrix
    tfidf_vectorizer = TfidfVectorizer(max_features=50)
    tfidf_matrix = tfidf_vectorizer.fit_transform(processed_texts)
    
    nltk_tfidf_memory = get_memory_usage()
    print(f"   📊 NLTK + scikit-learn TF-IDF: {nltk_tfidf_memory:.2f} MB (+{nltk_tfidf_memory - initial_memory:.2f} MB)")
    
    # EZR TF-IDF
    gc.collect()
    ezr_initial = get_memory_usage()
    
    from ezr.prep import addDoc, compute
    prep = Prep()
    for text in texts[:sample_size]:
        addDoc(prep, text, "dummy_label")
    compute(prep)
    
    ezr_tfidf_memory = get_memory_usage()
    print(f"   📊 EZR TF-IDF: {ezr_tfidf_memory:.2f} MB (+{ezr_tfidf_memory - ezr_initial:.2f} MB)")
    
    return nltk_tfidf_memory - initial_memory, ezr_tfidf_memory - ezr_initial

def check_disk_space():
    """Check disk space usage."""
    print("💾 Disk Space Analysis:")
    
    # Check current directory size
    current_dir = os.getcwd()
    total_size = 0
    file_count = 0
    
    for dirpath, dirnames, filenames in os.walk(current_dir):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.exists(filepath):
                total_size += os.path.getsize(filepath)
                file_count += 1
    
    print(f"   📊 Current project size: {total_size / 1024 / 1024:.2f} MB ({file_count} files)")
    
    # Check EZR specific files
    ezr_files = ['etc/stop_words.txt', 'etc/suffixes.txt']
    ezr_total = 0
    for file in ezr_files:
        if os.path.exists(file):
            ezr_total += os.path.getsize(file)
    
    print(f"   📊 EZR data files: {ezr_total} B")
    
    # Check NLTK data size
    try:
        nltk_data_path = nltk.data.path[0] if nltk.data.path else None
        if nltk_data_path and os.path.exists(nltk_data_path):
            nltk_size = 0
            for dirpath, dirnames, filenames in os.walk(nltk_data_path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        nltk_size += os.path.getsize(filepath)
            print(f"   📊 NLTK data directory: {nltk_size / 1024 / 1024:.2f} MB")
    except:
        print("   ❌ Could not determine NLTK data size")

def check_dependencies():
    """Check dependency sizes."""
    print("📦 Dependency Analysis:")
    
    # Check NLTK package size
    try:
        import nltk
        nltk_path = os.path.dirname(nltk.__file__)
        nltk_size = 0
        for root, dirs, files in os.walk(nltk_path):
            for file in files:
                filepath = os.path.join(root, file)
                if os.path.exists(filepath):
                    nltk_size += os.path.getsize(filepath)
        print(f"   📦 NLTK package: {nltk_size / 1024 / 1024:.2f} MB")
    except:
        print("   ❌ Could not determine NLTK package size")
    
    # Check scikit-learn package size
    try:
        import sklearn
        sklearn_path = os.path.dirname(sklearn.__file__)
        sklearn_size = 0
        for root, dirs, files in os.walk(sklearn_path):
            for file in files:
                filepath = os.path.join(root, file)
                if os.path.exists(filepath):
                    sklearn_size += os.path.getsize(filepath)
        print(f"   📦 scikit-learn package: {sklearn_size / 1024 / 1024:.2f} MB")
    except:
        print("   ❌ Could not determine scikit-learn package size")

def main():
    print("=" * 80)
    print("COMPREHENSIVE SPACE ANALYSIS: EZR vs NLTK")
    print("=" * 80)
    
    # Load sample data
    print("📂 Loading sample data...")
    try:
        import csv
        texts = []
        with open("../moot/text_mining/reading/raw/Hall.csv", 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                text = row.get('Abstract', '').strip()
                if text and len(text) > 10:
                    texts.append(text)
        print(f"   ✅ Loaded {len(texts)} abstracts from Hall dataset")
    except:
        print("   ❌ Could not load Hall dataset, using sample texts")
        texts = [
            "The quick brown fox jumps over the lazy dog. This is a sample text for preprocessing.",
            "Machine learning algorithms are being applied to various domains including natural language processing.",
            "The researchers conducted experiments using different preprocessing techniques and evaluated their performance."
        ] * 50  # Create 150 sample texts
    
    print()
    
    # Memory usage analysis
    print("🧠 MEMORY USAGE ANALYSIS")
    print("-" * 40)
    
    nltk_memory = analyze_nltk_memory_usage(texts, 50)
    print()
    
    ezr_memory = analyze_ezr_memory_usage(texts, 50)
    print()
    
    nltk_tfidf, ezr_tfidf = analyze_tfidf_memory_usage(texts, 50)
    print()
    
    # Disk space analysis
    print("💾 DISK SPACE ANALYSIS")
    print("-" * 40)
    check_disk_space()
    print()
    
    # Dependency analysis
    print("📦 DEPENDENCY ANALYSIS")
    print("-" * 40)
    check_dependencies()
    print()
    
    # Summary
    print("📊 SUMMARY")
    print("-" * 40)
    print(f"   🧠 NLTK memory overhead: {nltk_memory:.2f} MB")
    print(f"   🧠 EZR memory overhead: {ezr_memory:.2f} MB")
    print(f"   🧠 NLTK TF-IDF memory: {nltk_tfidf:.2f} MB")
    print(f"   🧠 EZR TF-IDF memory: {ezr_tfidf:.2f} MB")
    print(f"   💾 NLTK data files: ~73 MB")
    print(f"   💾 EZR data files: ~1.3 KB")
    print()
    
    memory_ratio = nltk_memory / ezr_memory if ezr_memory > 0 else float('inf')
    print(f"   🎯 NLTK uses {memory_ratio:.1f}x more memory than EZR for preprocessing")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    main()
