#!/usr/bin/env python3
"""
Extract archived CSV files for analysis.
Run this script to extract simulation_results.csv files from ZIP archives.
"""

import zipfile
import os
from pathlib import Path

def extract_csv_files(extract_to='temp_data'):
    """Extract all CSV files from ZIP archives."""
    
    data_dir = Path('data')
    extract_dir = Path(extract_to)
    extract_dir.mkdir(exist_ok=True)
    
    print("Extracting CSV files from archives...")
    print("=" * 50)
    
    zip_files = list(data_dir.glob('simulation_results_*.zip'))
    
    if not zip_files:
        print("ERROR: No ZIP files found in data/ directory")
        return {}
    
    extracted_files = {}
    
    for zip_path in zip_files:
        # Extract frequency from filename
        freq_part = zip_path.stem.replace('simulation_results_', '')
        
        print(f"Extracting {zip_path.name}...")
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                # Extract to frequency-specific directory
                freq_dir = extract_dir / freq_part
                freq_dir.mkdir(exist_ok=True)
                
                zipf.extractall(freq_dir)
                
                csv_file = freq_dir / 'simulation_results.csv'
                if csv_file.exists():
                    file_size = csv_file.stat().st_size
                    print(f"   SUCCESS: Extracted {csv_file} ({file_size:,} bytes)")
                    extracted_files[freq_part] = str(csv_file)
                else:
                    print(f"   ERROR: CSV file not found after extraction")
                    
        except Exception as e:
            print(f"   ERROR: Error extracting {zip_path.name}: {e}")
    
    print(f"\nExtraction complete! Files available in '{extract_to}/' directory")
    return extracted_files

def cleanup_extracted_files(extract_dir='temp_data'):
    """Clean up extracted files to save space."""
    import shutil
    
    if Path(extract_dir).exists():
        shutil.rmtree(extract_dir)
        print(f"Cleaned up extracted files in '{extract_dir}/'")

def get_csv_path(frequency, extract_dir='temp_data'):
    """Get path to extracted CSV for a specific frequency."""
    freq_map = {
        '600': '600mhz',
        '1000': '1000mhz', 
        '1600': '1600mhz',
        '2000': '2000mhz'
    }
    
    freq_key = freq_map.get(str(frequency), f'{frequency}mhz')
    return Path(extract_dir) / freq_key / 'simulation_results.csv'

if __name__ == "__main__":
    print("CSV Data Extraction Utility")
    print("=" * 40)
    
    # Extract files
    files = extract_csv_files()
    
    if files:
        print("\nExtracted files:")
        for freq, path in files.items():
            print(f"   {freq}: {path}")
        
        print("\nUsage in your scripts:")
        print("   from extract_data import extract_csv_files, get_csv_path")
        print("   files = extract_csv_files()")
        print("   csv_path = get_csv_path('600')  # for 600MHz data")
        
        # Optionally clean up (comment out if you want to keep files)
        # cleanup_extracted_files()
