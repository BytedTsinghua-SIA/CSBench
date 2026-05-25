"""
Comprehensive Test Runner for Problem Set 1

This script runs all tests and analyses for the peak-finding problem set:
- Problem 1-3: Correctness testing
- Problem 1-4: Complexity analysis
- Problem 1-6: Counterexample generation
"""

import sys
import os

# Add src directory to path if needed
if os.path.dirname(__file__) not in sys.path:
    sys.path.insert(0, os.path.dirname(__file__))

def main():
    """
    Run all tests and analyses for the problem set.
    """
    print("=" * 70)
    print("MIT 6.006 Problem Set 1 - Comprehensive Test Suite")
    print("=" * 70)
    print()
    
    # Import test modules
    try:
        import test_correctness
        print("Running Problem 1-3: Peak-Finding Correctness Tests...")
        print()
        test_correctness.testAllAlgorithms()
        print()
    except Exception as e:
        print(f"Error running correctness tests: {e}")
        print()
    
    print("\n" + "=" * 70 + "\n")
    
    try:
        import analyze_complexity
        print("Running Problem 1-4: Peak-Finding Efficiency Analysis...")
        print()
        analyze_complexity.analyzeComplexity()
        print()
    except Exception as e:
        print(f"Error running complexity analysis: {e}")
        print()
    
    print("\n" + "=" * 70 + "\n")
    
    try:
        import counterexample_generator
        print("Running Problem 1-6: Counterexample Generation...")
        print()
        counterexample_generator.generateAllCounterexamples()
        print()
    except Exception as e:
        print(f"Error running counterexample generator: {e}")
        print()
    
    print("=" * 70)
    print("All tests completed!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. Review the correctness test results to determine which algorithms are correct")
    print("2. Review the complexity analysis to determine runtime complexities")
    print("3. Use the generated counterexamples or create your own for incorrect algorithms")
    print("4. Fill in your answers in ps1_sol.tex according to the README.txt instructions")

if __name__ == "__main__":
    main()

