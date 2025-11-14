# Configuration System Documentation

This document describes the flexible data source configuration system for the Martini Simulation Analysis tools.

## 🎯 Overview

The configuration system provides automatic data source detection and fallback, supporting multiple file locations without code changes. It handles:

- **Network paths** (original Samba locations)
- **ZIP archives** (compressed local storage)
- **Local CSV directories** (custom file organization)
- **Custom paths** (user-defined locations)
- **Extracted files** (temporary extraction cache)

## 🚀 Quick Start

### Use the Universal Analyzer
```bash
python universal_analyzer.py
```
This automatically detects available data sources and runs analysis.

### Check Data Source Status
```bash
python config_manager.py
```
This shows all configured sources and their availability.

## 📋 Data Source Priority Order

The system tries sources in priority order (lower number = higher priority):

1. **Network Paths** (Priority 1) - Direct network access
2. **Local ZIP Archives** (Priority 2) - Auto-extracts from ZIP files  
3. **Extracted Files** (Priority 3) - Previously extracted ZIP contents
4. **Local CSV Directory** (Priority 4) - Organized local CSV files
5. **Custom Paths** (Priority 5) - User-defined locations

## 🔧 Configuration Management

### Interactive Setup
```bash
python universal_analyzer.py
# Choose option 1-4 in the setup menu to configure sources
```

### Programmatic Configuration
```python
from config_manager import config, add_custom_csv_location, set_csv_directory

# Add custom path for specific frequency
add_custom_csv_location("600MHz", "/path/to/600mhz_data.csv")

# Set local CSV directory
set_csv_directory("/path/to/csv/files")

# Add custom network location
config.add_custom_path("600MHz", "\\\\server\\share\\600mhz\\simulation_results.csv")
```

## 📁 File Organization Options

### Option 1: ZIP Archives (Recommended for repositories)
```
data/
├── simulation_results_600mhz.zip
├── simulation_results_1000mhz.zip
├── simulation_results_1600mhz.zip
└── simulation_results_2000mhz.zip
```

### Option 2: Local CSV Directory
```
local_csv/
├── simulation_results_600MHz.csv
├── simulation_results_1000MHz.csv
├── simulation_results_1600MHz.csv
└── simulation_results_2000MHz.csv
```

### Option 3: Custom Organization
```
my_data/
├── 600_freq/
│   └── simulation_results.csv
├── 1000_freq/
│   └── simulation_results.csv
├── 1600_freq/
│   └── simulation_results.csv
└── 2000_freq/
    └── simulation_results.csv
```

## 🛠️ Configuration File Structure

The `config.json` file contains:

```json
{
  "data_sources": {
    "network_paths": {
      "enabled": true,
      "priority": 1,
      "paths": {
        "600MHz": "\\\\server\\path\\600Mhz",
        "1000MHz": "\\\\server\\path\\1000Mhz",
        ...
      }
    },
    "local_zip_archives": {
      "enabled": true,
      "priority": 2,
      "base_path": "data",
      "extract_path": "temp_data",
      "files": {
        "600MHz": "simulation_results_600mhz.zip",
        ...
      }
    },
    ...
  },
  "analysis_settings": {
    "auto_extract_zip": true,
    "cleanup_extracted_files": false,
    "fallback_to_next_source": true,
    "verbose_logging": true
  }
}
```

## 📖 Usage Examples

### Example 1: Using with Network Access
```bash
# Network paths are available - uses them automatically
python universal_analyzer.py
```

### Example 2: Offline with ZIP Files
```bash
# Network unavailable - automatically extracts ZIP files
python universal_analyzer.py
```

### Example 3: Custom Local Directory
```bash
# Set up custom directory first
python -c "from config_manager import set_csv_directory; set_csv_directory('/my/csv/folder')"
python universal_analyzer.py
```

### Example 4: Mixed Sources
```python
from config_manager import config

# Add custom path for one frequency
config.add_custom_path("600MHz", "/special/location/600mhz_data.csv")

# Others will use default sources (network, ZIP, etc.)
```

## 🔍 Troubleshooting

### No Data Sources Found
```bash
# Check status
python config_manager.py

# Add custom location
python -c "from config_manager import add_custom_csv_location; add_custom_csv_location('600MHz', '/path/to/file.csv')"
```

### Network Issues
The system automatically falls back to ZIP archives if network paths are unavailable.

### Missing ZIP Files
```bash
# Create ZIP archives from network sources
python archive_csv_files.py
```

### Configuration Issues
```bash
# Reset to default configuration
rm config.json
python config_manager.py
```

## 🎛️ Advanced Configuration

### Disable Automatic ZIP Extraction
```python
from config_manager import config
config.config["analysis_settings"]["auto_extract_zip"] = False
config.save_config()
```

### Change Priority Order
```python
from config_manager import config
config.config["data_sources"]["local_csv_directory"]["priority"] = 1
config.save_config()
```

### Enable Cleanup of Extracted Files
```python
from config_manager import config
config.config["analysis_settings"]["cleanup_extracted_files"] = True
config.save_config()
```

## 🚀 Benefits

1. **📍 Location Independence**: Works regardless of where CSV files are stored
2. **🔄 Automatic Fallback**: Seamlessly switches between data sources
3. **⚙️ Easy Configuration**: Simple setup for different environments
4. **🎯 Smart Detection**: Automatically finds the best available source
5. **📦 ZIP Support**: Space-efficient storage with automatic extraction
6. **🔧 Extensible**: Easy to add new data source types

## 💡 Best Practices

1. **Keep ZIP archives**: Provides reliable offline access
2. **Use priority order**: Higher priority for faster/preferred sources
3. **Enable verbose logging**: Helps troubleshoot data source issues
4. **Regular status checks**: Run `config_manager.py` to verify setup
5. **Custom paths for exceptions**: Handle special cases without changing defaults