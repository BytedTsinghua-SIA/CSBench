#!/usr/bin/env python3
"""
Unit tests for TableTemplate functionality.
Each test is independent and covers specific functionality.
"""
import sys
import json
import subprocess
import os

def run_js_test(test_file):
    """Execute JavaScript test file and return result."""
    try:
        process = subprocess.run(
            ['node', test_file],
            capture_output=True,
            timeout=5,
            cwd=os.path.dirname(os.path.dirname(__file__))
        )
        output = process.stdout.decode('utf-8').strip()
        if process.returncode == 0:
            for line in output.split('\n'):
                line = line.strip()
                if line.startswith('{') and 'pass' in line:
                    try:
                        return json.loads(line)
                    except:
                        pass
            return {'pass': False, 'error': 'No valid output'}
        return {'pass': False, 'error': process.stderr.decode('utf-8')}
    except subprocess.TimeoutExpired:
        return {'pass': False, 'error': 'Timeout'}
    except Exception as e:
        return {'pass': False, 'error': str(e)}

def test_tabletemplate_class_exists():
    """Test that TableTemplate class exists."""
    jstests_dir = os.path.join(os.path.dirname(__file__), 'jstests')
    result = run_js_test(os.path.join(jstests_dir, 'test_tt_class.js'))
    assert result.get('pass', False), result.get('error', 'Test failed')

def test_tabletemplate_fillin_processes_header():
    """Test that fillIn processes header row template."""
    jstests_dir = os.path.join(os.path.dirname(__file__), 'jstests')
    result = run_js_test(os.path.join(jstests_dir, 'test_tt_header.js'))
    assert result.get('pass', False), result.get('error', 'Test failed')

def test_tabletemplate_fillin_handles_missing_table():
    """Test that fillIn handles missing table gracefully."""
    jstests_dir = os.path.join(os.path.dirname(__file__), 'jstests')
    result = run_js_test(os.path.join(jstests_dir, 'test_tt_missing.js'))
    assert result.get('pass', False), result.get('error', 'Test failed')

def test_tabletemplate_fillin_column_processing():
    """Test that fillIn processes specified column."""
    jstests_dir = os.path.join(os.path.dirname(__file__), 'jstests')
    result = run_js_test(os.path.join(jstests_dir, 'test_tt_column.js'))
    assert result.get('pass', False), result.get('error', 'Test failed')

def test_tabletemplate_visibility_update():
    """Test that fillIn updates table visibility."""
    jstests_dir = os.path.join(os.path.dirname(__file__), 'jstests')
    result = run_js_test(os.path.join(jstests_dir, 'test_tt_visibility.js'))
    assert result.get('pass', False), result.get('error', 'Test failed')

def test_tabletemplate_fillin_all_columns():
    """Test that fillIn processes all columns when columnName is not specified."""
    jstests_dir = os.path.join(os.path.dirname(__file__), 'jstests')
    result = run_js_test(os.path.join(jstests_dir, 'test_tt_all_columns.js'))
    assert result.get('pass', False), result.get('error', 'Test failed')

def test_tabletemplate_undefined_property():
    """Test that undefined properties are replaced with empty string."""
    jstests_dir = os.path.join(os.path.dirname(__file__), 'jstests')
    result = run_js_test(os.path.join(jstests_dir, 'test_tt_undefined_property.js'))
    assert result.get('pass', False), result.get('error', 'Test failed')

if __name__ == '__main__':
    import pytest
    sys.exit(pytest.main([__file__, '-v']))

