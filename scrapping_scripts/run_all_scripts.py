#!/usr/bin/env python3
"""
Script to run all scraping scripts in the scrapping_scripts directory.
"""
import os
import sys
import subprocess
from pathlib import Path

def run_all_scripts():
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    
    # Find all Python scripts (excluding this runner script)
    scripts = sorted([f for f in script_dir.glob("script_*.py") 
                     if f.name != "run_all_scripts.py"])
    
    if not scripts:
        print("No scripts found to run.")
        return
    
    print(f"Found {len(scripts)} scripts to run.\n")
    
    successful = []
    failed = []
    
    for idx, script in enumerate(scripts, 1):
        print(f"[{idx}/{len(scripts)}] Running {script.name}...")
        try:
            # Run the script using subprocess
            result = subprocess.run(
                [sys.executable, str(script)],
                cwd=str(script_dir),
                timeout=300,  # 5 minutes timeout per script
                check=True
            )
            print(f"✓ {script.name} completed successfully\n")
            successful.append(script.name)
        except subprocess.TimeoutExpired:
            print(f"✗ {script.name} timed out after 5 minutes\n")
            failed.append((script.name, "Timeout"))
        except subprocess.CalledProcessError as e:
            print(f"✗ {script.name} failed with error code {e.returncode}\n")
            failed.append((script.name, f"Error code: {e.returncode}"))
        except Exception as e:
            print(f"✗ {script.name} failed with error: {str(e)}\n")
            failed.append((script.name, str(e)))
    
    # Summary
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    print(f"Total scripts: {len(scripts)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")
    
    if successful:
        print("\nSuccessful scripts:")
        for script in successful:
            print(f"  ✓ {script}")
    
    if failed:
        print("\nFailed scripts:")
        for script, error in failed:
            print(f"  ✗ {script} - {error}")

if __name__ == "__main__":
    run_all_scripts()