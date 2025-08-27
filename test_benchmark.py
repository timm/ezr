#!/usr/bin/env python3
"""
Test script for the EZR vs NLTK benchmark
"""

import sys
import os

# Add the ezr package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ezr'))

try:
    from ezr.tm import eg__benchmark_preprocessing
    print("Starting EZR vs NLTK benchmark test...")
    eg__benchmark_preprocessing()
    print("Benchmark test completed successfully!")
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you have NLTK installed: pip install nltk")
except Exception as e:
    print(f"Error running benchmark: {e}")
    import traceback
    traceback.print_exc()
