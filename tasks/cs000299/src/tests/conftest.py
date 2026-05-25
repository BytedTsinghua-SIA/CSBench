"""
Shared test configuration and utilities
"""

import sys
import os
import pytest

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def try_import_implementation(module_name, class_name):
    """
    Try to import an implementation class, return None if not available
    """
    try:
        module = __import__(module_name, fromlist=[class_name])
        return getattr(module, class_name, None)
    except (ImportError, AttributeError):
        return None


@pytest.fixture
def implementation_available(request):
    """
    Fixture to check if implementation is available
    """
    module_name = request.param.get('module', 'lab_two_implementations')
    class_name = request.param.get('class')
    impl = try_import_implementation(module_name, class_name)
    return impl is not None

