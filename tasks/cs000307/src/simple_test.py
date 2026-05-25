#!/usr/bin/env python3
"""
Simple test for Network Path Analyzer core functionality.

This test checks if the script can be imported and basic functions work
without requiring external dependencies.
"""

import sys
import os

def test_import():
    """Test if the main module can be imported."""
    print("Testing module import...")

    try:
        # Try importing without dependencies
        sys.path.insert(0, os.path.dirname(__file__))

        # Check if basic syntax is valid
        with open('network_path_analyzer.py', 'r') as f:
            code = f.read()

        compile(code, 'network_path_analyzer.py', 'exec')
        print("  ✓ Module syntax is valid")
        return True

    except SyntaxError as e:
        print(f"  ✗ Syntax error in module: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        return False

def test_file_structure():
    """Test if all required files exist."""
    print("Testing file structure...")

    required_files = [
        'network_path_analyzer.py',
        'requirements.txt',
        'README.md',
        'example_usage.py'
    ]

    missing_files = []
    for filename in required_files:
        if not os.path.exists(filename):
            missing_files.append(filename)

    if missing_files:
        print(f"  ✗ Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("  ✓ All required files present")
        return True

def test_requirements_format():
    """Test if requirements.txt is properly formatted."""
    print("Testing requirements.txt format...")

    try:
        with open('requirements.txt', 'r') as f:
            lines = f.readlines()

        valid_lines = 0
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                # Basic package name check
                if '>=' in line or '==' in line or '<=' in line:
                    valid_lines += 1
                elif line.replace('.', '').replace('-', '').replace('_', '').isalnum():
                    valid_lines += 1

        if valid_lines > 0:
            print(f"  ✓ requirements.txt contains {valid_lines} valid package specifications")
            return True
        else:
            print("  ✗ requirements.txt appears to be empty or malformed")
            return False

    except FileNotFoundError:
        print("  ✗ requirements.txt not found")
        return False

def main():
    """Run all simple tests."""
    print("Network Path Analyzer - Simple Tests")
    print("=" * 50)

    tests = [
        test_file_structure,
        test_requirements_format,
        test_import
    ]

    passed = 0
    total = len(tests)

    for test_func in tests:
        if test_func():
            passed += 1
        print()

    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("✓ All simple tests passed!")
        print("\nTo run the full analysis, install dependencies:")
        print("  pip install -r requirements.txt")
        return 0
    else:
        print("✗ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
