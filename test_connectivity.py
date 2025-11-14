#!/usr/bin/env python3
"""
Quick test script to verify network connectivity and CSV file structure.
Run this before the main analysis to identify any issues.
"""

import os
import pandas as pd
from pathlib import Path

def test_network_connectivity():
    """Test connectivity to all network paths."""
    paths = {
        '600MHz': r'\\samba.zsc3.intel.com\nfs\site\disks\fsintel\disk_001\apattnay\martini_wa\llama4-8tp-600Mhz',
        '1000MHz': r'\\samba.zsc3.intel.com\nfs\site\disks\fsintel\disk_001\apattnay\martini_wa\llama4-8tp-1000Mhz',
        '1600MHz': r'\\samba.zsc3.intel.com\nfs\site\disks\fsintel\disk_001\apattnay\martini_wa\llama4-8tp-1600Mhz',
        '2000MHz': r'\\samba.zsc3.intel.com\nfs\site\disks\fsintel\disk_001\apattnay\martini_wa\llama4-8tp-2000Mhz'
    }
    
    print("Testing Network Connectivity...")
    print("=" * 50)
    
    for freq, path in paths.items():
        print(f"\n{freq}: {path}")
        if os.path.exists(path):
            print("  ✓ Directory accessible")
            
            csv_file = os.path.join(path, 'simulation_results.csv')
            if os.path.exists(csv_file):
                print("  ✓ simulation_results.csv found")
                
                # Check file size
                try:
                    file_size = os.path.getsize(csv_file)
                    print(f"  ✓ File size: {file_size:,} bytes")
                    
                    # Try to read first few rows
                    df = pd.read_csv(csv_file, nrows=5)
                    print(f"  ✓ File readable, columns: {list(df.columns)}")
                    
                    # Check for required columns
                    required_cols = ['RESOURCE', 'DURATION', 'TRANSITION']
                    missing_cols = [col for col in required_cols if col not in df.columns]
                    if missing_cols:
                        print(f"  ⚠ Missing columns: {missing_cols}")
                    else:
                        print("  ✓ All required columns present")
                        
                    # Check for gt/* resources
                    full_df = pd.read_csv(csv_file)
                    gt_count = full_df['RESOURCE'].str.startswith('gt/', na=False).sum()
                    print(f"  ✓ GT resources found: {gt_count}/{len(full_df)} rows")
                    
                except Exception as e:
                    print(f"  ✗ Error reading CSV: {e}")
            else:
                print("  ✗ simulation_results.csv not found")
        else:
            print("  ✗ Directory not accessible")

def test_sample_analysis():
    """Run a quick sample analysis on the first available CSV."""
    paths = {
        '600MHz': r'\\samba.zsc3.intel.com\nfs\site\disks\fsintel\disk_001\apattnay\martini_wa\llama4-8tp-600Mhz',
        '1000MHz': r'\\samba.zsc3.intel.com\nfs\site\disks\fsintel\disk_001\apattnay\martini_wa\llama4-8tp-1000Mhz',
        '1600MHz': r'\\samba.zsc3.intel.com\nfs\site\disks\fsintel\disk_001\apattnay\martini_wa\llama4-8tp-1600Mhz',
        '2000MHz': r'\\samba.zsc3.intel.com\nfs\site\disks\fsintel\disk_001\apattnay\martini_wa\llama4-8tp-2000Mhz'
    }
    
    print("\n\nRunning Sample Analysis...")
    print("=" * 50)
    
    for freq, path in paths.items():
        csv_file = os.path.join(path, 'simulation_results.csv')
        if os.path.exists(csv_file):
            try:
                print(f"\nAnalyzing {freq}...")
                df = pd.read_csv(csv_file)
                
                print(f"Total rows: {len(df)}")
                print(f"Columns: {list(df.columns)}")
                
                if 'RESOURCE' in df.columns:
                    gt_mask = df['RESOURCE'].str.startswith('gt/', na=False)
                    gt_df = df[gt_mask]
                    print(f"GT/* resources: {len(gt_df)} rows")
                    
                    if len(gt_df) > 0:
                        print(f"Sample GT resources: {gt_df['RESOURCE'].head(3).tolist()}")
                        
                        if 'DURATION' in df.columns:
                            gt_df['DURATION'] = pd.to_numeric(gt_df['DURATION'], errors='coerce')
                            total_duration = gt_df['DURATION'].sum()
                            print(f"Total duration for GT resources: {total_duration}")
                        
                        if 'TRANSITION' in df.columns:
                            unique_transitions = gt_df['TRANSITION'].nunique()
                            print(f"Unique transitions: {unique_transitions}")
                            print(f"Sample transitions: {gt_df['TRANSITION'].head(3).tolist()}")
                
                break  # Only test the first available file
                
            except Exception as e:
                print(f"Error analyzing {freq}: {e}")
                continue

if __name__ == "__main__":
    print("Simulation Analysis Pre-flight Check")
    print("=" * 60)
    
    test_network_connectivity()
    test_sample_analysis()
    
    print("\n" + "=" * 60)
    print("Pre-flight check complete!")
    print("If all tests passed, you can run: python simulation_analyzer.py")