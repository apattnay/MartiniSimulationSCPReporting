# Martini Simulation SCP Reporting

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A comprehensive analysis tool for Martini simulation results, focusing on GT/* resource analysis and LLM performance projections across different frequency sweeps.

## 🎯 Overview

This repository contains tools to analyze simulation_results.csv files from multiple frequency directories (600MHz, 1000MHz, 1600MHz, 2000MHz), filter GT/* resources, and project LLM token generation performance (TTFT + TPOT).

## 📊 Key Features

- **Multi-Frequency Analysis**: Process CSV files from 4 different frequency sweeps
- **GT Resource Filtering**: Automatically filters for resources matching 'gt/*' patterns  
- **Duration Analysis**: Calculate total, average, median, and statistical summaries
- **Transition Analysis**: Group and analyze data by transition types
- **LLM Performance Projection**: Project TTFT and TPOT based on simulation data
- **Comprehensive Reporting**: Generate Excel/CSV reports and visualizations

## Directory Structure

The tool expects simulation_results.csv files in these network locations:
- `\\samba.zsc3.intel.com\nfs\site\disks\fsintel\disk_001\apattnay\martini_wa\llama4-8tp-600Mhz\`
- `\\samba.zsc3.intel.com\nfs\site\disks\fsintel\disk_001\apattnay\martini_wa\llama4-8tp-1000Mhz\`
- `\\samba.zsc3.intel.com\nfs\site\disks\fsintel\disk_001\apattnay\martini_wa\llama4-8tp-1600Mhz\`
- `\\samba.zsc3.intel.com\nfs\site\disks\fsintel\disk_001\apattnay\martini_wa\llama4-8tp-2000Mhz\`

## Installation

1. Install required packages:
   ```powershell
   pip install -r requirements.txt
   ```

## Usage

### Quick Start

#### 🚀 **Recommended: Universal Analyzer**
```powershell
# Smart data source detection with automatic fallback
python universal_analyzer.py

# Check data source status
python config_manager.py
```

#### 🔧 **Alternative Methods**
```powershell
# Original ZIP-enabled analyzer
python auto_analyzer_zip.py

# Test network connectivity first (optional)
python test_connectivity.py

# Generate performance projections
python performance_projector.py

# Create visualizations
python simple_chart.py

# Generate comprehensive summary
python create_summary.py
```

### 🔧 **Flexible Data Source Configuration**

The tools automatically detect and use multiple data source types:

```powershell
# 1. Check what data sources are available
python config_manager.py

# 2. Add custom CSV locations
python -c "from config_manager import add_custom_csv_location; add_custom_csv_location('600MHz', '/your/path/data.csv')"

# 3. Set local CSV directory
python -c "from config_manager import set_csv_directory; set_csv_directory('/your/csv/folder')"

# 4. Create ZIP archives from network sources
python archive_csv_files.py

# 5. Extract ZIP files manually (usually automatic)
python extract_data.py
```

**📋 Supported Data Sources** (automatic priority order):
1. **🌐 Network paths** - Original Samba network locations
2. **📦 ZIP archives** - Compressed local files (auto-extraction)
3. **📁 Local CSV directory** - Organized local files
4. **🔧 Custom paths** - User-defined locations

### Custom Analysis

Use the SimulationAnalyzer class in your own scripts:

```python
from simulation_analyzer import SimulationAnalyzer

# Create analyzer instance
analyzer = SimulationAnalyzer()

# Run analysis for all frequencies
results = analyzer.run_analysis()

# Create summary report
summary = analyzer.create_summary_report()
print(summary)

# Export results
analyzer.export_results("my_output_folder")

# Create visualizations
analyzer.create_visualizations("my_output_folder")
```

## Expected CSV Format

The tool expects CSV files with these columns:
- **RESOURCE**: Resource identifier (filters for entries starting with 'gt/')
- **DURATION**: Numeric duration values to be summed and analyzed
- **TRANSITION**: Transition types for grouping and analysis

## Output Files

The tool generates several output files in the `output/` directory:

### Summary Files
- `frequency_sweep_summary.xlsx/csv`: Overall summary across all frequencies

### Per-Frequency Files
- `{frequency}_transition_analysis.xlsx/csv`: Detailed transition analysis
- `{frequency}_filtered_data.xlsx/csv`: Raw filtered data for each frequency

### Visualizations
- `duration_by_frequency.png`: Bar chart comparing total durations
- `{frequency}_top_transitions.png`: Top transitions by duration for each frequency

## Analysis Details

### Resource Filtering
- Filters rows where RESOURCE column starts with 'gt/'
- Reports count of filtered vs total rows

### Duration Analysis
For each frequency sweep, calculates:
- Total duration sum
- Average duration
- Median duration
- Standard deviation
- Min/Max values
- Row count

### Transition Analysis
Groups filtered data by TRANSITION column and provides:
- Count of occurrences
- Sum of durations
- Average duration
- Statistical measures per transition type

## Error Handling

The tool handles common issues:
- Missing CSV files
- Network connectivity issues
- Invalid data formats
- Missing columns

Error details are included in the summary report.

## Troubleshooting

### Network Access Issues
Ensure you have access to the network paths. Test connectivity:
```powershell
Test-Path "\\samba.zsc3.intel.com\nfs\site\disks\fsintel\disk_001\apattnay\martini_wa\llama4-8tp-600Mhz\"
```

### Missing Dependencies
Install all required packages:
```powershell
pip install pandas numpy matplotlib seaborn openpyxl
```

### Permission Issues
Run PowerShell as administrator if you encounter permission errors accessing network drives.