"""Tests for feature selection utilities."""

import os
import tempfile
import pytest
import pandas as pd
from pathlib import Path
from feature_selection import preview_csv, data_preview_generate


def test_preview_csv():
    """Test CSV preview generation."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("col1,col2,col3\n1,2,3\n4,5,6\n")
        csv_path = Path(f.name)
    
    try:
        preview = preview_csv(csv_path)
        
        assert "rows" in preview.lower()
        assert "columns" in preview.lower()
        assert "col1" in preview
        assert "col2" in preview
        assert "col3" in preview
    finally:
        os.unlink(csv_path)


def test_data_preview_generate():
    """Test data preview generation for directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test CSV files
        df1 = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        df2 = pd.DataFrame({"x": [5, 6], "y": [7, 8]})
        
        csv1_path = Path(tmpdir) / "file1.csv"
        csv2_path = Path(tmpdir) / "file2.csv"
        
        df1.to_csv(csv1_path, index=False)
        df2.to_csv(csv2_path, index=False)
        
        preview = data_preview_generate(tmpdir)
        
        assert "file1.csv" in preview or "file1" in preview
        assert "file2.csv" in preview or "file2" in preview
        assert "a" in preview or "b" in preview
        assert "x" in preview or "y" in preview


def test_preview_csv_numeric_stats():
    """Test that numeric column statistics are included."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("numeric_col,text_col\n1.5,hello\n2.5,world\n3.5,test\n")
        csv_path = Path(f.name)
    
    try:
        preview = preview_csv(csv_path)
        
        assert "numeric_col" in preview
        # Should include some statistics
        assert "min" in preview.lower() or "max" in preview.lower() or "mean" in preview.lower()
    finally:
        os.unlink(csv_path)

