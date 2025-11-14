#!/usr/bin/env python3
"""
Archive source CSV files from network locations to local ZIP files for repository storage.
"""

import os
import zipfile
import shutil
from pathlib import Path

def archive_csv_files():
    """Archive simulation_results.csv files from network locations."""
    
    # Source paths
    source_paths = {
        '600MHz': r'\\samba.zsc3.intel.com\nfs\site\disks\fsintel\disk_001\apattnay\martini_wa\llama4-8tp-600Mhz',
        '1000MHz': r'\\samba.zsc3.intel.com\nfs\site\disks\fsintel\disk_001\apattnay\martini_wa\llama4-8tp-1000Mhz',
        '1600MHz': r'\\samba.zsc3.intel.com\nfs\site\disks\fsintel\disk_001\apattnay\martini_wa\llama4-8tp-1600Mhz',
        '2000MHz': r'\\samba.zsc3.intel.com\nfs\site\disks\fsintel\disk_001\apattnay\martini_wa\llama4-8tp-2000Mhz'
    }
    
    # Create data directory
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    
    print("🗜️ Archiving CSV files to ZIP format...")
    print("=" * 60)
    
    archived_files = []
    
    for freq, path in source_paths.items():
        csv_file = os.path.join(path, 'simulation_results.csv')
        zip_filename = f'simulation_results_{freq.lower()}.zip'
        zip_path = data_dir / zip_filename
        
        print(f"\n📁 Processing {freq}...")
        
        if not os.path.exists(csv_file):
            print(f"❌ CSV file not found: {csv_file}")
            continue
        
        try:
            # Get file size
            file_size = os.path.getsize(csv_file)
            print(f"   Original size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
            
            # Create ZIP archive
            print(f"   Creating ZIP: {zip_filename}")
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
                zipf.write(csv_file, 'simulation_results.csv')
            
            # Check compressed size
            compressed_size = zip_path.stat().st_size
            compression_ratio = (1 - compressed_size / file_size) * 100
            
            print(f"   ✅ Compressed size: {compressed_size:,} bytes ({compressed_size/1024/1024:.1f} MB)")
            print(f"   📊 Compression: {compression_ratio:.1f}% reduction")
            
            archived_files.append({
                'frequency': freq,
                'zip_file': zip_filename,
                'original_size': file_size,
                'compressed_size': compressed_size,
                'compression_ratio': compression_ratio
            })
            
        except Exception as e:
            print(f"   ❌ Error archiving {freq}: {e}")
    
    # Create summary
    if archived_files:
        print("\n" + "=" * 60)
        print("📋 ARCHIVING SUMMARY")
        print("=" * 60)
        
        total_original = sum(f['original_size'] for f in archived_files)
        total_compressed = sum(f['compressed_size'] for f in archived_files)
        overall_compression = (1 - total_compressed / total_original) * 100
        
        for file_info in archived_files:
            print(f"✅ {file_info['frequency']:>8}: {file_info['zip_file']} "
                  f"({file_info['compressed_size']/1024/1024:.1f} MB, {file_info['compression_ratio']:.1f}% reduction)")
        
        print(f"\n📊 TOTAL COMPRESSION:")
        print(f"   Original: {total_original:,} bytes ({total_original/1024/1024:.1f} MB)")
        print(f"   Compressed: {total_compressed:,} bytes ({total_compressed/1024/1024:.1f} MB)")
        print(f"   Overall reduction: {overall_compression:.1f}%")
        
        # Create data extraction script
        create_extraction_script()
        
        print(f"\n💾 Files saved to 'data/' directory")
        print("📄 Created 'extract_data.py' for data extraction")
        
    return archived_files

def create_extraction_script():
    """Create a script to extract ZIP files when needed."""
    
    script_content = '''#!/usr/bin/env python3
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
    
    print("📦 Extracting CSV files from archives...")
    print("=" * 50)
    
    zip_files = list(data_dir.glob('simulation_results_*.zip'))
    
    if not zip_files:
        print("❌ No ZIP files found in data/ directory")
        return {}
    
    extracted_files = {}
    
    for zip_path in zip_files:
        # Extract frequency from filename
        freq_part = zip_path.stem.replace('simulation_results_', '')
        
        print(f"📁 Extracting {zip_path.name}...")
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                # Extract to frequency-specific directory
                freq_dir = extract_dir / freq_part
                freq_dir.mkdir(exist_ok=True)
                
                zipf.extractall(freq_dir)
                
                csv_file = freq_dir / 'simulation_results.csv'
                if csv_file.exists():
                    file_size = csv_file.stat().st_size
                    print(f"   ✅ Extracted: {csv_file} ({file_size:,} bytes)")
                    extracted_files[freq_part] = str(csv_file)
                else:
                    print(f"   ❌ CSV file not found after extraction")
                    
        except Exception as e:
            print(f"   ❌ Error extracting {zip_path.name}: {e}")
    
    print(f"\\n✅ Extraction complete! Files available in '{extract_to}/' directory")
    return extracted_files

def cleanup_extracted_files(extract_dir='temp_data'):
    """Clean up extracted files to save space."""
    import shutil
    
    if Path(extract_dir).exists():
        shutil.rmtree(extract_dir)
        print(f"🧹 Cleaned up extracted files in '{extract_dir}/'")

if __name__ == "__main__":
    print("🎯 CSV Data Extraction Utility")
    print("=" * 40)
    
    # Extract files
    files = extract_csv_files()
    
    if files:
        print("\\n📋 Extracted files:")
        for freq, path in files.items():
            print(f"   {freq}: {path}")
        
        print("\\n💡 Usage in your scripts:")
        print("   from extract_data import extract_csv_files")
        print("   files = extract_csv_files()")
        print("   # Use files dictionary to access CSV paths")
        
        # Optionally clean up (comment out if you want to keep files)
        # cleanup_extracted_files()
'''
    
    with open('extract_data.py', 'w') as f:
        f.write(script_content)

if __name__ == "__main__":
    archived_files = archive_csv_files()
    
    if archived_files:
        print("\n🎯 Next steps:")
        print("1. Add the 'data/' directory to git: git add data/")
        print("2. Commit the changes: git commit -m 'Add archived CSV source data'") 
        print("3. Push to repository: git push")
        print("\n💡 To extract data later, run: python extract_data.py")