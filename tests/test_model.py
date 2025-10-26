"""
Test suite for model training and prediction functionality
"""

import pytest
import pandas as pd
import numpy as np
import os
import sys
import tempfile
import shutil

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from train import load_data, preprocess, get_git_sha

class TestDataProcessing:
    """Test data loading and preprocessing"""
    
    def test_load_data(self):
        """Test data loading function"""
        df = load_data()
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert 'target' in df.columns
        
        # Check expected columns
        expected_cols = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 
                        'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal', 'target']
        assert list(df.columns) == expected_cols
        
    def test_preprocess(self):
        """Test preprocessing function"""
        # Create sample data
        sample_data = {
            'age': [50, 45, 60, 55],
            'sex': [1, 0, 1, 0],
            'cp': [0, 1, 2, 1],
            'trestbps': [120, 130, 140, 110],
            'chol': [200, 220, 180, 240],
            'fbs': [0, 1, 0, 1],
            'restecg': [0, 1, 0, 1],
            'thalach': [150, 160, 140, 170],
            'exang': [0, 1, 0, 0],
            'oldpeak': [1.0, 2.0, 1.5, 0.5],
            'slope': [2, 1, 2, 1],
            'ca': [0, 1, 2, 0],
            'thal': [2, 3, 2, 3],
            'target': [0, 1, 1, 0]
        }
        df = pd.DataFrame(sample_data)
        
        X, y = preprocess(df)
        
        assert isinstance(X, pd.DataFrame)
        assert isinstance(y, pd.Series)
        assert len(X) == len(y)
        assert len(X) > 0
        assert 'target' not in X.columns
        assert set(y.unique()).issubset({0, 1})
        
    def test_git_sha_function(self):
        """Test git SHA retrieval"""
        sha = get_git_sha()
        assert isinstance(sha, str)
        assert len(sha) > 0

class TestModelValidation:
    """Test model validation and performance"""
    
    def test_model_performance_threshold(self):
        """Test that model meets minimum performance threshold"""
        # This would be implemented with actual model training
        # For now, we'll create a placeholder test
        expected_min_accuracy = 0.7
        # actual_accuracy = train_and_evaluate_model()
        # assert actual_accuracy >= expected_min_accuracy
        assert True  # Placeholder
        
    def test_model_prediction_format(self):
        """Test that model predictions are in correct format"""
        # This would test actual model predictions
        # For now, we'll create a placeholder test
        assert True  # Placeholder
        
class TestDataQuality:
    """Test data quality and validation"""
    
    def test_data_completeness(self):
        """Test that data has required completeness"""
        df = load_data()
        
        # After preprocessing, should have reasonable amount of data
        X, y = preprocess(df)
        assert len(X) >= 200, "Dataset should have at least 200 samples after preprocessing"
        
    def test_target_distribution(self):
        """Test target variable distribution"""
        df = load_data()
        X, y = preprocess(df)
        
        # Check that target is binary
        unique_targets = y.unique()
        assert len(unique_targets) == 2, "Target should be binary"
        assert set(unique_targets) == {0, 1}, "Target should be 0 and 1"
        
        # Check for reasonable class balance (not too imbalanced)
        class_counts = y.value_counts()
        minority_ratio = min(class_counts) / max(class_counts)
        assert minority_ratio >= 0.2, "Classes should not be too imbalanced"
        
    def test_feature_ranges(self):
        """Test that features are within expected ranges"""
        df = load_data()
        X, y = preprocess(df)
        
        # Basic range checks for some features
        if 'age' in X.columns:
            assert X['age'].min() >= 0, "Age should be non-negative"
            assert X['age'].max() <= 120, "Age should be reasonable"
            
        if 'sex' in X.columns:
            assert set(X['sex'].unique()).issubset({0, 1}), "Sex should be binary"