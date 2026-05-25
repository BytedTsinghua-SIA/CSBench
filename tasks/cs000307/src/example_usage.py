#!/usr/bin/env python3
"""
Example usage of the Network Path Analyzer

This script demonstrates how to use the network_path_analyzer.py
to analyze ping data collected from Internet paths.

Before running:
1. Install dependencies: pip install -r requirements.txt
2. Collect ping data: ping -D -n -i 0.2 example.com | tee ping_example.txt
3. Optionally collect traceroute data: traceroute example.com > traceroute_example.txt
4. Run analysis: python network_path_analyzer.py ping_example.txt --traceroute-file traceroute_example.txt
"""

import subprocess
import time
from pathlib import Path

def collect_sample_data(target_host: str = "8.8.8.8", duration_minutes: int = 1):
    """
    Collect sample ping data for demonstration.

    Args:
        target_host: Target host to ping
        duration_minutes: How long to collect data (in minutes)
    """
    print(f"Collecting ping data from {target_host} for {duration_minutes} minute(s)...")

    # Calculate number of pings (5 per second * 60 seconds * minutes)
    num_pings = 5 * 60 * duration_minutes

    # Run ping command
    cmd = [
        'ping', '-D', '-n', '-i', '0.2', '-c', str(num_pings), target_host
    ]

    ping_file = f"ping_{target_host.replace('.', '_')}.txt"
    try:
        with open(ping_file, 'w') as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, timeout=duration_minutes*60 + 10)
        print(f"Ping data saved to {ping_file}")
        return ping_file
    except subprocess.TimeoutExpired:
        print("Ping collection timed out")
        return None
    except FileNotFoundError:
        print("Error: ping command not found. Make sure you're on a Unix-like system.")
        return None

def collect_traceroute_data(target_host: str = "8.8.8.8"):
    """
    Collect traceroute data for path analysis.

    Args:
        target_host: Target host to trace
    """
    print(f"Collecting traceroute data to {target_host}...")

    traceroute_file = f"traceroute_{target_host.replace('.', '_')}.txt"
    try:
        with open(traceroute_file, 'w') as f:
            result = subprocess.run(['traceroute', target_host], stdout=f, stderr=subprocess.STDOUT, timeout=60)
        print(f"Traceroute data saved to {traceroute_file}")
        return traceroute_file
    except subprocess.TimeoutExpired:
        print("Traceroute timed out")
        return None
    except FileNotFoundError:
        print("Error: traceroute command not found. Try using 'mtr' instead.")
        return None

def main():
    """Demonstrate the complete analysis workflow."""
    print("Network Path Analyzer - Example Usage")
    print("=" * 50)

    # Example targets (you can modify these)
    targets = [
        "8.8.8.8",  # Google DNS
        "www.ox.ac.uk",  # Oxford University
        "www.canterbury.ac.nz"  # University of Canterbury
    ]

    for target in targets:
        print(f"\nAnalyzing path to {target}")
        print("-" * 30)

        # Collect data (uncomment to actually collect data)
        # ping_file = collect_sample_data(target, duration_minutes=1)
        # traceroute_file = collect_traceroute_data(target)

        # For demonstration, assume files exist
        ping_file = f"ping_{target.replace('.', '_')}.txt"
        traceroute_file = f"traceroute_{target.replace('.', '_')}.txt"

        # Check if files exist
        if not Path(ping_file).exists():
            print(f"Ping data file {ping_file} not found. Skipping analysis for {target}.")
            continue

        # Run analysis
        print(f"Running analysis on {ping_file}...")

        try:
            # Import and run the analyzer
            from network_path_analyzer import NetworkPathAnalyzer

            analyzer = NetworkPathAnalyzer(
                ping_file=ping_file,
                traceroute_file=traceroute_file if Path(traceroute_file).exists() else None,
                output_dir=f"analysis_{target.replace('.', '_')}"
            )

            analyzer.run_complete_analysis()

        except ImportError as e:
            print(f"Error importing analyzer: {e}")
            print("Make sure to install dependencies: pip install -r requirements.txt")
        except Exception as e:
            print(f"Analysis failed for {target}: {e}")

if __name__ == "__main__":
    main()
