#!/usr/bin/env python3
"""
Configuration manager for Martini Simulation Analysis Tools.
Handles multiple data source locations and provides flexible path resolution.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Union

class DataSourceConfig:
    """Configuration manager for data sources and file locations."""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict:
        """Load configuration from file or create default."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Error loading config file: {e}")
                return self.get_default_config()
        else:
            config = self.get_default_config()
            self.save_config(config)
            return config
    
    def save_config(self, config: Optional[Dict] = None):
        """Save configuration to file."""
        if config is None:
            config = self.config
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"✅ Configuration saved to {self.config_file}")
        except Exception as e:
            print(f"❌ Error saving config: {e}")
    
    def get_default_config(self) -> Dict:
        """Get default configuration with multiple data source options."""
        return {
            "data_sources": {
                "network_paths": {
                    "enabled": True,
                    "priority": 1,
                    "paths": {
                        "600MHz": r"\\samba.zsc3.intel.com\nfs\site\disks\fsintel\disk_001\apattnay\martini_wa\llama4-8tp-600Mhz",
                        "1000MHz": r"\\samba.zsc3.intel.com\nfs\site\disks\fsintel\disk_001\apattnay\martini_wa\llama4-8tp-1000Mhz",
                        "1600MHz": r"\\samba.zsc3.intel.com\nfs\site\disks\fsintel\disk_001\apattnay\martini_wa\llama4-8tp-1600Mhz",
                        "2000MHz": r"\\samba.zsc3.intel.com\nfs\site\disks\fsintel\disk_001\apattnay\martini_wa\llama4-8tp-2000Mhz"
                    }
                },
                "local_zip_archives": {
                    "enabled": True,
                    "priority": 2,
                    "base_path": "data",
                    "extract_path": "temp_data",
                    "files": {
                        "600MHz": "simulation_results_600mhz.zip",
                        "1000MHz": "simulation_results_1000mhz.zip",
                        "1600MHz": "simulation_results_1600mhz.zip",
                        "2000MHz": "simulation_results_2000mhz.zip"
                    }
                },
                "extracted_files": {
                    "enabled": True,
                    "priority": 3,
                    "base_path": "temp_data",
                    "subdirs": {
                        "600MHz": "600mhz",
                        "1000MHz": "1000mhz",
                        "1600MHz": "1600mhz",
                        "2000MHz": "2000mhz"
                    }
                },
                "local_csv_directory": {
                    "enabled": True,
                    "priority": 4,
                    "base_path": "local_csv",
                    "files": {
                        "600MHz": "simulation_results_600MHz.csv",
                        "1000MHz": "simulation_results_1000MHz.csv",
                        "1600MHz": "simulation_results_1600MHz.csv",
                        "2000MHz": "simulation_results_2000MHz.csv"
                    }
                },
                "custom_paths": {
                    "enabled": True,
                    "priority": 5,
                    "paths": {}
                }
            },
            "analysis_settings": {
                "auto_extract_zip": True,
                "cleanup_extracted_files": False,
                "fallback_to_next_source": True,
                "verbose_logging": True
            }
        }
    
    def add_custom_path(self, frequency: str, path: str):
        """Add a custom path for a specific frequency."""
        if "custom_paths" not in self.config["data_sources"]:
            self.config["data_sources"]["custom_paths"] = {
                "enabled": True,
                "priority": 5,
                "paths": {}
            }
        
        self.config["data_sources"]["custom_paths"]["paths"][frequency] = path
        self.save_config()
        print(f"✅ Added custom path for {frequency}: {path}")
    
    def set_local_csv_directory(self, directory_path: str):
        """Set the local CSV directory path."""
        self.config["data_sources"]["local_csv_directory"]["base_path"] = directory_path
        self.save_config()
        print(f"✅ Set local CSV directory: {directory_path}")
    
    def get_csv_file_path(self, frequency: str) -> Optional[str]:
        """
        Get the CSV file path for a frequency, trying all configured sources in priority order.
        """
        if self.config["analysis_settings"]["verbose_logging"]:
            print(f"🔍 Searching for {frequency} CSV file...")
        
        # Get all data sources sorted by priority
        sources = sorted(
            [(name, config) for name, config in self.config["data_sources"].items() if config.get("enabled", False)],
            key=lambda x: x[1].get("priority", 999)
        )
        
        for source_name, source_config in sources:
            if self.config["analysis_settings"]["verbose_logging"]:
                print(f"   Trying source: {source_name} (priority {source_config.get('priority', 'N/A')})")
            
            try:
                csv_path = self._try_source(frequency, source_name, source_config)
                if csv_path and os.path.exists(csv_path):
                    if self.config["analysis_settings"]["verbose_logging"]:
                        print(f"   ✅ Found: {csv_path}")
                    return csv_path
                elif csv_path:
                    if self.config["analysis_settings"]["verbose_logging"]:
                        print(f"   ❌ Path exists but file not found: {csv_path}")
            except Exception as e:
                if self.config["analysis_settings"]["verbose_logging"]:
                    print(f"   ❌ Error with {source_name}: {e}")
                
            if not self.config["analysis_settings"]["fallback_to_next_source"]:
                break
        
        print(f"❌ No CSV file found for {frequency}")
        return None
    
    def _try_source(self, frequency: str, source_name: str, source_config: Dict) -> Optional[str]:
        """Try to get CSV path from a specific source."""
        
        if source_name == "network_paths":
            if frequency in source_config["paths"]:
                return os.path.join(source_config["paths"][frequency], "simulation_results.csv")
        
        elif source_name == "local_zip_archives":
            if frequency in source_config["files"]:
                # Check if we need to extract
                zip_path = os.path.join(source_config["base_path"], source_config["files"][frequency])
                if os.path.exists(zip_path):
                    if self.config["analysis_settings"]["auto_extract_zip"]:
                        extracted_path = self._extract_zip_file(zip_path, source_config["extract_path"], frequency)
                        return extracted_path
                    else:
                        print(f"   ZIP file found but auto-extraction disabled: {zip_path}")
        
        elif source_name == "extracted_files":
            if frequency in source_config["subdirs"]:
                subdir = source_config["subdirs"][frequency]
                return os.path.join(source_config["base_path"], subdir, "simulation_results.csv")
        
        elif source_name == "local_csv_directory":
            if frequency in source_config["files"]:
                return os.path.join(source_config["base_path"], source_config["files"][frequency])
        
        elif source_name == "custom_paths":
            if frequency in source_config.get("paths", {}):
                custom_path = source_config["paths"][frequency]
                # If it's a directory, append filename
                if os.path.isdir(custom_path):
                    return os.path.join(custom_path, "simulation_results.csv")
                else:
                    return custom_path
        
        return None
    
    def _extract_zip_file(self, zip_path: str, extract_base: str, frequency: str) -> Optional[str]:
        """Extract ZIP file and return CSV path."""
        try:
            import zipfile
            from pathlib import Path
            
            # Determine extract directory
            freq_mapping = {
                '600MHz': '600mhz',
                '1000MHz': '1000mhz', 
                '1600MHz': '1600mhz',
                '2000MHz': '2000mhz'
            }
            
            freq_folder = freq_mapping.get(frequency, frequency.lower())
            extract_dir = Path(extract_base) / freq_folder
            extract_dir.mkdir(parents=True, exist_ok=True)
            
            csv_file = extract_dir / "simulation_results.csv"
            
            # Extract only if CSV doesn't exist or ZIP is newer
            if not csv_file.exists() or os.path.getmtime(zip_path) > os.path.getmtime(csv_file):
                print(f"   📦 Extracting {zip_path}...")
                with zipfile.ZipFile(zip_path, 'r') as zipf:
                    zipf.extractall(extract_dir)
                print(f"   ✅ Extracted to {extract_dir}")
            
            return str(csv_file) if csv_file.exists() else None
            
        except Exception as e:
            print(f"   ❌ Error extracting ZIP: {e}")
            return None
    
    def list_available_sources(self) -> Dict[str, Dict]:
        """List all available data sources and their status."""
        sources_status = {}
        
        for source_name, source_config in self.config["data_sources"].items():
            if not source_config.get("enabled", False):
                continue
                
            status = {
                "enabled": source_config.get("enabled", False),
                "priority": source_config.get("priority", 999),
                "frequencies": {}
            }
            
            for freq in ["600MHz", "1000MHz", "1600MHz", "2000MHz"]:
                try:
                    path = self._try_source(freq, source_name, source_config)
                    if path:
                        exists = os.path.exists(path)
                        status["frequencies"][freq] = {
                            "path": path,
                            "exists": exists,
                            "size": os.path.getsize(path) if exists else 0
                        }
                    else:
                        status["frequencies"][freq] = {
                            "path": None,
                            "exists": False,
                            "size": 0
                        }
                except:
                    status["frequencies"][freq] = {
                        "path": None,
                        "exists": False,
                        "size": 0
                    }
            
            sources_status[source_name] = status
        
        return sources_status
    
    def print_status_report(self):
        """Print a comprehensive status report of all data sources."""
        print("\n" + "="*80)
        print("📊 DATA SOURCES STATUS REPORT")
        print("="*80)
        
        sources = self.list_available_sources()
        
        for source_name, status in sources.items():
            print(f"\n🔧 {source_name.upper().replace('_', ' ')}")
            print(f"   Priority: {status['priority']}, Enabled: {status['enabled']}")
            print("   " + "-" * 50)
            
            for freq, freq_status in status["frequencies"].items():
                icon = "✅" if freq_status["exists"] else "❌"
                size_mb = freq_status["size"] / 1024 / 1024 if freq_status["size"] > 0 else 0
                print(f"   {icon} {freq:>8}: {freq_status['path'] or 'N/A'}")
                if freq_status["exists"] and size_mb > 0:
                    print(f"            Size: {size_mb:.1f} MB")
        
        print(f"\n💡 Configuration file: {self.config_file}")
        print("   Use config.add_custom_path() to add new locations")

# Global instance
config = DataSourceConfig()

def get_csv_path(frequency: str) -> Optional[str]:
    """Convenience function to get CSV path for a frequency."""
    return config.get_csv_file_path(frequency)

def add_custom_csv_location(frequency: str, path: str):
    """Convenience function to add custom CSV location."""
    config.add_custom_path(frequency, path)

def set_csv_directory(directory: str):
    """Convenience function to set local CSV directory."""
    config.set_local_csv_directory(directory)

if __name__ == "__main__":
    # Demo the configuration system
    print("🎯 Data Source Configuration Demo")
    config.print_status_report()