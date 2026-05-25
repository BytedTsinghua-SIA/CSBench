"""
Helper module for running Julia functions from Python tests.
"""
import json
import subprocess
import os
from typing import Any, List, Optional


class JuliaRunner:
    """Wrapper for executing Julia functions and parsing results."""
    
    def __init__(self, julia_script: str = None):
        """
        Initialize Julia runner.
        
        Args:
            julia_script: Path to Julia test interface script
        """
        if julia_script is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            julia_script = os.path.join(script_dir, "test_interface.jl")
        self.julia_script = julia_script
    
    def _run_julia(self, func_name: str, *args: str) -> dict:
        """
        Execute Julia function and return result.
        
        Args:
            func_name: Name of Julia function to call
            *args: Arguments to pass to Julia function
            
        Returns:
            Dictionary with result or error
        """
        cmd = ["julia", self.julia_script, func_name] + list(args)
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                check=True
            )
            output = result.stdout.strip()
            return json.loads(output)
        except subprocess.TimeoutExpired:
            return {"error": "Timeout"}
        except subprocess.CalledProcessError as e:
            return {"error": f"Julia error: {e.stderr}"}
        except json.JSONDecodeError:
            return {"error": "Invalid JSON response"}
    
    def call_sum1(self, x: List[float]) -> Optional[float]:
        """Call sum1 function."""
        x_json = json.dumps(x)
        result = self._run_julia("sum1", x_json)
        return result.get("result")
    
    def call_sum2(self, x: List[float]) -> Optional[float]:
        """Call sum2 function."""
        x_json = json.dumps(x)
        result = self._run_julia("sum2", x_json)
        return result.get("result")
    
    def call_sum3(self, x: List[float]) -> Optional[float]:
        """Call sum3 function."""
        x_json = json.dumps(x)
        result = self._run_julia("sum3", x_json)
        return result.get("result")
    
    def call_rela_error(self, x: float, xhat: float) -> Optional[float]:
        """Call rela_error function."""
        result = self._run_julia("rela_error", str(x), str(xhat))
        return result.get("result")
    
    def call_naive_phi(self, x: float) -> Optional[float]:
        """Call naive_phi function."""
        result = self._run_julia("naive_phi", str(x))
        return result.get("result")
    
    def call_stable_phi(self, x: float) -> Optional[float]:
        """Call stable_phi function."""
        result = self._run_julia("stable_phi", str(x))
        return result.get("result")
    
    def call_condition_number_phi(self, x: float) -> Optional[float]:
        """Call condition_number_phi function."""
        result = self._run_julia("condition_number_phi", str(x))
        return result.get("result")
    
    def call_lagrange_cardinal(self, t: List[float], x: float, k: int) -> Optional[float]:
        """Call lagrange_cardinal function."""
        t_json = json.dumps(t)
        result = self._run_julia("lagrange_cardinal", t_json, str(x), str(k))
        return result.get("result")
    
    def call_lagrange_interpolant(self, t: List[float], y: List[float], x: float) -> Optional[float]:
        """Call lagrange_interpolant function."""
        t_json = json.dumps(t)
        y_json = json.dumps(y)
        result = self._run_julia("lagrange_interpolant", t_json, y_json, str(x))
        return result.get("result")
    
    def call_chebyshev_points(self, n: int) -> Optional[List[float]]:
        """Call chebyshev_points function."""
        result = self._run_julia("chebyshev_points", str(n))
        return result.get("result")

