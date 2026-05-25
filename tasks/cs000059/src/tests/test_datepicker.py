#!/usr/bin/env python3
"""
Unit tests for DatePicker functionality.
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

def test_datepicker_constructor_exists():
    """Test that DatePicker constructor exists."""
    jstests_dir = os.path.join(os.path.dirname(__file__), 'jstests')
    result = run_js_test(os.path.join(jstests_dir, 'test_dp_constructor.js'))
    assert result.get('pass', False), result.get('error', 'Test failed')

def test_datepicker_render_creates_html():
    """Test that render method creates HTML structure."""
    jstests_dir = os.path.join(os.path.dirname(__file__), 'jstests')
    result = run_js_test(os.path.join(jstests_dir, 'test_dp_render.js'))
    assert result.get('pass', False), result.get('error', 'Test failed')

def test_datepicker_callback_invoked():
    """Test that callback is invoked with correct format."""
    jstests_dir = os.path.join(os.path.dirname(__file__), 'jstests')
    result = run_js_test(os.path.join(jstests_dir, 'test_dp_callback.js'))
    assert result.get('pass', False), result.get('error', 'Test failed')

def test_datepicker_calendar_structure():
    """Test that calendar has correct structure."""
    jstests_dir = os.path.join(os.path.dirname(__file__), 'jstests')
    result = run_js_test(os.path.join(jstests_dir, 'test_dp_structure.js'))
    assert result.get('pass', False), result.get('error', 'Test failed')

def test_datepicker_month_navigation():
    """Test that month navigation buttons exist."""
    jstests_dir = os.path.join(os.path.dirname(__file__), 'jstests')
    result = run_js_test(os.path.join(jstests_dir, 'test_dp_navigation.js'))
    assert result.get('pass', False), result.get('error', 'Test failed')

def test_datepicker_handles_invalid_container():
    """Test that render handles missing container gracefully."""
    jstests_dir = os.path.join(os.path.dirname(__file__), 'jstests')
    result = run_js_test(os.path.join(jstests_dir, 'test_dp_invalid.js'))
    assert result.get('pass', False), result.get('error', 'Test failed')

def test_datepicker_other_month_no_callback():
    """Test that clicking other month days does not trigger callback."""
    jstests_dir = os.path.join(os.path.dirname(__file__), 'jstests')
    result = run_js_test(os.path.join(jstests_dir, 'test_dp_other_month_no_callback.js'))
    assert result.get('pass', False), result.get('error', 'Test failed')

if __name__ == '__main__':
    import pytest
    sys.exit(pytest.main([__file__, '-v']))

