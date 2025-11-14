# Archived Simulation Data

This directory contains compressed CSV files from the Martini simulation results.

## 📦 ZIP Archive Contents

| File | Original Size | Compressed Size | Compression Ratio | Description |
|------|---------------|----------------|-------------------|-------------|
| `simulation_results_600mhz.zip` | 60.0 MB | 8.7 MB | 85.6% reduction | 600MHz frequency sweep data |
| `simulation_results_1000mhz.zip` | 59.6 MB | 8.6 MB | 85.5% reduction | 1000MHz frequency sweep data |
| `simulation_results_1600mhz.zip` | 59.3 MB | 8.4 MB | 85.9% reduction | 1600MHz frequency sweep data |
| `simulation_results_2000mhz.zip` | 59.5 MB | 8.4 MB | 85.8% reduction | 2000MHz frequency sweep data |

**Total Space Savings**: 238.5 MB → 34.1 MB (85.7% reduction)

## 🚀 Usage

### Automatic Extraction
The analysis tools will automatically extract these files when network paths are unavailable:

```python
python auto_analyzer_zip.py
```

### Manual Extraction
To manually extract all ZIP files:

```python
python extract_data.py
```

### Extract in Code
```python
from extract_data import extract_csv_files, get_csv_path

# Extract all files
files = extract_csv_files()

# Get specific frequency path
csv_path = get_csv_path('600')  # Returns path to 600MHz CSV
```

## 📋 Original Source Locations

The CSV files were archived from these network locations:

- **600MHz**: `\\samba.zsc3.intel.com\nfs\site\disks\fsintel\disk_001\apattnay\martini_wa\llama4-8tp-600Mhz\simulation_results.csv`
- **1000MHz**: `\\samba.zsc3.intel.com\nfs\site\disks\fsintel\disk_001\apattnay\martini_wa\llama4-8tp-1000Mhz\simulation_results.csv`
- **1600MHz**: `\\samba.zsc3.intel.com\nfs\site\disks\fsintel\disk_001\apattnay\martini_wa\llama4-8tp-1600Mhz\simulation_results.csv`
- **2000MHz**: `\\samba.zsc3.intel.com\nfs\site\disks\fsintel\disk_001\apattnay\martini_wa\llama4-8tp-2000Mhz\simulation_results.csv`

## 📊 CSV File Structure

Each CSV file contains the following columns:
- **READY**: Timestamp when resource became ready
- **START**: Simulation start timestamp
- **FINISH**: Simulation finish timestamp
- **TRANSITION**: Transition identifier (unique per operation)
- **RESOURCE**: Resource identifier (analysis filters for 'gt/*' patterns)
- **RESOURCE_IDX**: Resource index number
- **DURATION**: Duration of the operation (target of analysis)

## 🔄 Updating Archives

To update the archives with new simulation data:

```python
python archive_csv_files.py
```

This will:
1. Check for updated CSV files in the network locations
2. Create new compressed archives
3. Preserve the existing ZIP format structure

## 💾 Storage Efficiency

- Original CSV files: ~60MB each (240MB total)
- Compressed ZIP files: ~8.5MB each (34MB total) 
- **Space savings**: 85.7% reduction in repository size
- **Benefits**: Faster git operations, reduced bandwidth, easier distribution