#!/usr/bin/env python3
"""
Hardware Configuration Manager - Enhanced configuration management system
Supports creating, updating, and browsing multiple hardware configurations.
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import shutil

class HardwareConfigManager:
    """Enhanced configuration manager for hardware projections."""
    
    def __init__(self, config_dir: str = "hardware_configs"):
        self.config_dir = config_dir
        self.ensure_config_directory()
        self.current_config_file = None
        self.current_config = None
        
    def ensure_config_directory(self):
        """Create config directory if it doesn't exist."""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
            print(f"📁 Created hardware configs directory: {self.config_dir}")
    
    def list_available_configs(self) -> List[Dict[str, Any]]:
        """List all available hardware configuration files."""
        configs = []
        
        # Check for default config in current directory
        if os.path.exists("hardware_projection_config.json"):
            try:
                with open("hardware_projection_config.json", 'r') as f:
                    config_data = json.load(f)
                configs.append({
                    'filename': "hardware_projection_config.json",
                    'path': "hardware_projection_config.json",
                    'name': "Default Configuration",
                    'current_hw': config_data['hardware_settings']['current_hardware']['name'],
                    'future_hw': config_data['hardware_settings']['future_hardware']['name'],
                    'description': f"{config_data['hardware_settings']['current_hardware']['name']} → {config_data['hardware_settings']['future_hardware']['name']}",
                    'is_default': True,
                    'created_date': config_data.get('metadata', {}).get('created_date', 'Unknown')
                })
            except Exception as e:
                print(f"⚠️ Error reading default config: {e}")
        
        # Check for configs in config directory
        for filename in os.listdir(self.config_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.config_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        config_data = json.load(f)
                    
                    # Extract metadata
                    metadata = config_data.get('metadata', {})
                    hw_settings = config_data.get('hardware_settings', {})
                    current_hw = hw_settings.get('current_hardware', {}).get('name', 'Unknown')
                    future_hw = hw_settings.get('future_hardware', {}).get('name', 'Unknown')
                    
                    configs.append({
                        'filename': filename,
                        'path': filepath,
                        'name': metadata.get('name', filename.replace('.json', '')),
                        'current_hw': current_hw,
                        'future_hw': future_hw,
                        'description': metadata.get('description', f"{current_hw} → {future_hw}"),
                        'created_date': metadata.get('created_date', 'Unknown'),
                        'version': metadata.get('version', '1.0'),
                        'is_default': False
                    })
                except Exception as e:
                    print(f"⚠️ Error reading {filename}: {e}")
        
        return configs
    
    def display_config_browser(self) -> Optional[str]:
        """Interactive browser for selecting hardware configurations."""
        configs = self.list_available_configs()
        
        if not configs:
            print("❌ No hardware configurations found!")
            return None
        
        print("\n" + "="*90)
        print("🔧 Hardware Configuration Browser")
        print("="*90)
        
        print(f"{'#':<3} {'Name':<20} {'Current HW':<10} {'Future HW':<10} {'Description':<25} {'Date':<12}")
        print("-" * 90)
        
        for i, config in enumerate(configs, 1):
            default_marker = "📌" if config['is_default'] else "  "
            date_str = config['created_date'][:10] if config['created_date'] != 'Unknown' else 'Unknown'
            print(f"{i:<3} {config['name'][:19]:<20} {config['current_hw']:<10} {config['future_hw']:<10} {config['description'][:24]:<25} {date_str:<12} {default_marker}")
        
        print("-" * 90)
        print("Options:")
        print("  Enter number to select configuration")
        print("  'n' or 'new' - Create new configuration")
        print("  'u' or 'update' - Update existing configuration")
        print("  'q' or 'quit' - Return to main menu")
        
        while True:
            choice = input("\nSelect option: ").strip().lower()
            
            if choice in ['q', 'quit']:
                return None
            elif choice in ['n', 'new']:
                return self.create_new_hardware_config()
            elif choice in ['u', 'update']:
                return self.select_config_for_update(configs)
            else:
                try:
                    config_idx = int(choice) - 1
                    if 0 <= config_idx < len(configs):
                        selected_config = configs[config_idx]
                        print(f"\n✅ Selected: {selected_config['name']}")
                        return selected_config['path']
                    else:
                        print(f"❌ Invalid selection. Choose 1-{len(configs)}")
                except ValueError:
                    print("❌ Invalid input. Enter a number, 'new', 'update', or 'quit'")
    
    def select_config_for_update(self, configs: List[Dict]) -> Optional[str]:
        """Select a configuration to update."""
        print("\n🔧 Select Configuration to Update:")
        print("-" * 40)
        
        for i, config in enumerate(configs, 1):
            print(f"{i}. {config['name']} ({config['current_hw']} → {config['future_hw']})")
        
        while True:
            try:
                choice = input("Select configuration number to update: ").strip()
                if choice.lower() in ['q', 'quit', 'cancel']:
                    return None
                    
                config_idx = int(choice) - 1
                if 0 <= config_idx < len(configs):
                    selected_config = configs[config_idx]
                    updated = self.update_existing_config(selected_config['path'])
                    if updated:
                        return selected_config['path']
                    else:
                        return None
                else:
                    print(f"❌ Invalid selection. Choose 1-{len(configs)}")
            except ValueError:
                print("❌ Invalid input. Enter a number or 'quit'")
    
    def create_new_hardware_config(self) -> Optional[str]:
        """Interactive creation of new hardware configuration."""
        print("\n" + "="*60)
        print("🛠️ Create New Hardware Configuration")
        print("="*60)
        
        # Get basic metadata
        config_name = input("Configuration name: ").strip()
        if not config_name:
            print("❌ Configuration name is required!")
            return None
            
        description = input("Description (optional): ").strip()
        
        # Get current hardware info
        print("\n📊 Current Hardware Settings:")
        current_hw_name = input("Current hardware name (e.g., PVC): ").strip() or "PVC"
        current_hw_desc = input("Current hardware description: ").strip() or f"{current_hw_name} Current Generation"
        
        # Get baseline measurements
        print("\n⏱️ Baseline Performance Measurements:")
        try:
            ttft_ms = float(input("TTFT (ms) [8336]: ") or "8336")
            tpot_ms = float(input("TPOT (ms) [53.46]: ") or "53.46")
            baseline_freq = int(input("Baseline frequency (MHz) [1600]: ") or "1600")
            tokens_input = int(input("Input tokens [112]: ") or "112")
            tokens_output = int(input("Output tokens [2]: ") or "2")
        except ValueError:
            print("❌ Invalid numeric input!")
            return None
        
        # Get future hardware info
        print("\n🚀 Future Hardware Settings:")
        future_hw_name = input("Future hardware name (e.g., JGS): ").strip() or "JGS"
        future_hw_desc = input("Future hardware description: ").strip() or f"{future_hw_name} Next Generation"
        
        # Get improvement factors
        print("\n📈 Hardware Improvement Factors:")
        print("(Enter improvement factors - lower values mean better performance for time ratios)")
        print("⚠️  All values must be greater than 0 to avoid division by zero errors!")
        
        # XeCore compute improvement with validation
        while True:
            try:
                xecore_input = input("XeCore compute improvement (time ratio, e.g., 0.375 for 37.5% faster) [0.375]: ").strip()
                xecore_factor = float(xecore_input) if xecore_input else 0.375
                if xecore_factor <= 0:
                    print("❌ XeCore compute improvement must be greater than 0")
                    continue
                break
            except ValueError:
                print("❌ Please enter a valid number")
        
        # HBM bandwidth improvement with validation
        while True:
            try:
                hbm_input = input("HBM bandwidth multiplier (e.g., 6.5 for 6.5x faster) [6.5]: ").strip()
                hbm_bandwidth = float(hbm_input) if hbm_input else 6.5
                if hbm_bandwidth <= 0:
                    print("❌ HBM bandwidth multiplier must be greater than 0")
                    continue
                break
            except ValueError:
                print("❌ Please enter a valid number")
        
        # Fabrication process improvement with validation
        while True:
            try:
                fab_input = input("Fabrication process improvement (time ratio, e.g., 0.75 for 25% gain) [0.75]: ").strip()
                fabrication = float(fab_input) if fab_input else 0.75
                if fabrication <= 0:
                    print("❌ Fabrication process improvement must be greater than 0")
                    continue
                break
            except ValueError:
                print("❌ Please enter a valid number")
        
        # Communication bandwidth improvement with validation
        while True:
            try:
                comm_bw_input = input("Communication bandwidth multiplier [12.5]: ").strip()
                comm_bandwidth = float(comm_bw_input) if comm_bw_input else 12.5
                if comm_bandwidth <= 0:
                    print("❌ Communication bandwidth multiplier must be greater than 0")
                    continue
                break
            except ValueError:
                print("❌ Please enter a valid number")
        
        # Communication latency improvement with validation
        while True:
            try:
                comm_lat_input = input("Communication latency improvement multiplier [150]: ").strip()
                comm_latency = float(comm_lat_input) if comm_lat_input else 150
                if comm_latency <= 0:
                    print("❌ Communication latency improvement multiplier must be greater than 0")
                    continue
                break
            except ValueError:
                print("❌ Please enter a valid number")
        
        # Create configuration structure
        config_data = self._create_config_structure(
            config_name, description, current_hw_name, current_hw_desc,
            ttft_ms, tpot_ms, baseline_freq, tokens_input, tokens_output,
            future_hw_name, future_hw_desc, xecore_factor, hbm_bandwidth,
            fabrication, comm_bandwidth, comm_latency
        )
        
        # Save configuration
        filename = f"{config_name.replace(' ', '_').lower()}_config.json"
        filepath = os.path.join(self.config_dir, filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            print(f"\n✅ Configuration saved: {filepath}")
            self._display_config_summary(config_data, current_hw_name, future_hw_name, 
                                       xecore_factor, hbm_bandwidth, fabrication, 
                                       comm_bandwidth, comm_latency)
            
            return filepath
            
        except Exception as e:
            print(f"❌ Error saving configuration: {e}")
            return None
    
    def _create_config_structure(self, config_name, description, current_hw_name, current_hw_desc,
                               ttft_ms, tpot_ms, baseline_freq, tokens_input, tokens_output,
                               future_hw_name, future_hw_desc, xecore_factor, hbm_bandwidth,
                               fabrication, comm_bandwidth, comm_latency):
        """Create the complete configuration data structure."""
        return {
            "metadata": {
                "name": config_name,
                "description": description or f"{current_hw_name} to {future_hw_name} projection",
                "version": "1.0",
                "created_date": datetime.now().isoformat(),
                "created_by": "Hardware Config Manager"
            },
            "hardware_settings": {
                "current_hardware": {
                    "name": current_hw_name,
                    "description": current_hw_desc,
                    "baseline_measurements": {
                        "ttft_ms": ttft_ms,
                        "tpot_ms": tpot_ms,
                        "baseline_frequency": baseline_freq,
                        "tokens_input": tokens_input,
                        "tokens_output": tokens_output
                    }
                },
                "future_hardware": {
                    "name": future_hw_name,
                    "description": future_hw_desc,
                    "improvement_factors": {
                        "xecore_compute": {
                            "value": xecore_factor,
                            "description": "Compute improvement (time ratio - lower is better)",
                            "applies_to": ["compute_tasks"],
                            "configurable": True
                        },
                        "hbm_bandwidth": {
                            "value": hbm_bandwidth,
                            "description": f"{hbm_bandwidth}x higher memory bandwidth (throughput multiplier)",
                            "applies_to": ["memory_tasks"],
                            "configurable": True
                        },
                        "fabrication_process": {
                            "value": fabrication,
                            "description": "Performance gain from process improvement (time ratio)",
                            "applies_to": ["all_tasks"],
                            "configurable": True
                        },
                        "communication": {
                            "bandwidth_improvement": {
                                "value": comm_bandwidth,
                                "description": f"{comm_bandwidth}x communication bandwidth improvement"
                            },
                            "latency_improvement": {
                                "value": comm_latency,
                                "description": f"{comm_latency}x lower communication latency"
                            },
                            "applies_to": ["communication_tasks"],
                            "configurable": True
                        }
                    }
                }
            },
            "calculation_settings": {
                "enabled_approaches": [
                    "hardware_calibrated",
                    "pure_simulation", 
                    "hybrid_correlation"
                ],
                "execution_options": {
                    "run_single_approach": False,
                    "run_all_approaches": True,
                    "default_single_approach": "hybrid_correlation"
                },
                "simulation_correlation": {
                    "correlation_factor": 8.611e-7,
                    "calibration_method": "hardware_baseline",
                    "configurable": True
                },
                "resource_distribution": {
                    "ex_u1_split": {
                        "memory_copy": 0.30,
                        "communication": 0.70,
                        "configurable": True
                    },
                    "fallback_weights": {
                        "compute": 0.4,
                        "memory": 0.3,
                        "communication": 0.3,
                        "configurable": True
                    }
                }
            },
            "multi_gpu_settings": {
                "configurations": {
                    "8T": {"gpus": 4, "tiles_per_gpu": 2, "description": "4 GPU configuration with 8 tiles"},
                    "16T": {"gpus": 8, "tiles_per_gpu": 2, "description": "8 GPU configuration with 16 tiles"},
                    "144T": {"gpus": 72, "tiles_per_gpu": 2, "description": "72 GPU configuration with 144 tiles"}
                },
                "scaling_efficiency": {
                    "compute_scaling": 0.95,
                    "memory_scaling": 0.90,
                    "communication_overhead": 0.85,
                    "configurable": True
                }
            },
            "output_settings": {
                "generate_visualizations": True,
                "export_detailed_results": True,
                "comparison_tables": True,
                "performance_summary": True,
                "output_formats": ["csv", "json", "html"]
            }
        }
    
    def _display_config_summary(self, config_data, current_hw_name, future_hw_name, 
                              xecore_factor, hbm_bandwidth, fabrication, 
                              comm_bandwidth, comm_latency):
        """Display a summary of the created configuration."""
        print(f"📊 Hardware: {current_hw_name} → {future_hw_name}")
        print(f"📈 Key Improvements:")
        print(f"   Compute: {(1/xecore_factor-1)*100:.1f}% faster")
        print(f"   Memory: {hbm_bandwidth:.1f}x bandwidth")
        print(f"   Process: {(1/fabrication-1)*100:.1f}% gain")
        print(f"   Communication: {comm_bandwidth:.1f}x bandwidth, {comm_latency:.0f}x lower latency")
    
    def update_existing_config(self, config_path: str) -> bool:
        """Update an existing hardware configuration."""
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            return False
        
        print(f"\n🔧 Update Configuration: {os.path.basename(config_path)}")
        print("="*60)
        
        # Show current settings
        current_hw = config_data['hardware_settings']['current_hardware']
        future_hw = config_data['hardware_settings']['future_hardware']
        
        print(f"📊 Current Hardware: {current_hw['name']} - {current_hw['description']}")
        print(f"🚀 Future Hardware: {future_hw['name']} - {future_hw['description']}")
        
        print("\nWhat would you like to update?")
        print("1. Baseline measurements (TTFT, TPOT, tokens)")
        print("2. Hardware improvement factors")
        print("3. Hardware names and descriptions")
        print("4. Calculation settings")
        print("5. All of the above (guided update)")
        print("q. Cancel")
        
        choice = input("\nSelect option: ").strip().lower()
        
        if choice == '1':
            return self._update_baseline_measurements(config_data, config_path)
        elif choice == '2':
            return self._update_improvement_factors(config_data, config_path)
        elif choice == '3':
            return self._update_hardware_info(config_data, config_path)
        elif choice == '4':
            return self._update_calculation_settings(config_data, config_path)
        elif choice == '5':
            return self._guided_full_update(config_data, config_path)
        else:
            print("❌ Update cancelled")
            return False
    
    def _update_baseline_measurements(self, config_data: Dict, config_path: str) -> bool:
        """Update baseline performance measurements."""
        baseline = config_data['hardware_settings']['current_hardware']['baseline_measurements']
        
        print("\n⏱️ Update Baseline Measurements:")
        print(f"Current values:")
        print(f"  TTFT: {baseline['ttft_ms']} ms")
        print(f"  TPOT: {baseline['tpot_ms']} ms") 
        print(f"  Frequency: {baseline['baseline_frequency']} MHz")
        print(f"  Input tokens: {baseline['tokens_input']}")
        print(f"  Output tokens: {baseline['tokens_output']}")
        
        try:
            ttft = input(f"New TTFT (ms) [{baseline['ttft_ms']}]: ").strip()
            if ttft:
                baseline['ttft_ms'] = float(ttft)
                
            tpot = input(f"New TPOT (ms) [{baseline['tpot_ms']}]: ").strip()
            if tpot:
                baseline['tpot_ms'] = float(tpot)
                
            freq = input(f"New baseline frequency (MHz) [{baseline['baseline_frequency']}]: ").strip()
            if freq:
                baseline['baseline_frequency'] = int(freq)
                
            tokens_in = input(f"New input tokens [{baseline['tokens_input']}]: ").strip()
            if tokens_in:
                baseline['tokens_input'] = int(tokens_in)
                
            tokens_out = input(f"New output tokens [{baseline['tokens_output']}]: ").strip()
            if tokens_out:
                baseline['tokens_output'] = int(tokens_out)
                
        except ValueError:
            print("❌ Invalid numeric input!")
            return False
        
        return self._save_config(config_data, config_path)
    
    def _update_improvement_factors(self, config_data: Dict, config_path: str) -> bool:
        """Update hardware improvement factors."""
        factors = config_data['hardware_settings']['future_hardware']['improvement_factors']
        
        print("\n📈 Update Hardware Improvement Factors:")
        print("⚠️  All values must be greater than 0 to avoid division by zero errors!")
        
        # XeCore compute with validation
        while True:
            try:
                current_xecore = factors['xecore_compute']['value']
                new_xecore = input(f"XeCore compute improvement (time ratio) [{current_xecore}]: ").strip()
                if new_xecore:
                    value = float(new_xecore)
                    if value <= 0:
                        print("❌ XeCore compute improvement must be greater than 0")
                        continue
                    factors['xecore_compute']['value'] = value
                break
            except ValueError:
                print("❌ Please enter a valid number")
        
        # HBM bandwidth with validation
        while True:
            try:
                current_hbm = factors['hbm_bandwidth']['value']
                new_hbm = input(f"HBM bandwidth multiplier [{current_hbm}]: ").strip()
                if new_hbm:
                    value = float(new_hbm)
                    if value <= 0:
                        print("❌ HBM bandwidth multiplier must be greater than 0")
                        continue
                    factors['hbm_bandwidth']['value'] = value
                break
            except ValueError:
                print("❌ Please enter a valid number")
        
        # Fabrication with validation
        while True:
            try:
                current_fab = factors['fabrication_process']['value']
                new_fab = input(f"Fabrication process improvement (time ratio) [{current_fab}]: ").strip()
                if new_fab:
                    value = float(new_fab)
                    if value <= 0:
                        print("❌ Fabrication process improvement must be greater than 0")
                        continue
                    factors['fabrication_process']['value'] = value
                break
            except ValueError:
                print("❌ Please enter a valid number")
        
        # Communication bandwidth with validation
        while True:
            try:
                current_comm_bw = factors['communication']['bandwidth_improvement']['value']
                new_comm_bw = input(f"Communication bandwidth multiplier [{current_comm_bw}]: ").strip()
                if new_comm_bw:
                    value = float(new_comm_bw)
                    if value <= 0:
                        print("❌ Communication bandwidth multiplier must be greater than 0")
                        continue
                    factors['communication']['bandwidth_improvement']['value'] = value
                break
            except ValueError:
                print("❌ Please enter a valid number")
        
        # Communication latency with validation
        while True:
            try:
                current_comm_lat = factors['communication']['latency_improvement']['value']
                new_comm_lat = input(f"Communication latency improvement multiplier [{current_comm_lat}]: ").strip()
                if new_comm_lat:
                    value = float(new_comm_lat)
                    if value <= 0:
                        print("❌ Communication latency improvement multiplier must be greater than 0")
                        continue
                    factors['communication']['latency_improvement']['value'] = value
                break
            except ValueError:
                print("❌ Please enter a valid number")
        
        return self._save_config(config_data, config_path)
    
    def _update_hardware_info(self, config_data: Dict, config_path: str) -> bool:
        """Update hardware names and descriptions."""
        current_hw = config_data['hardware_settings']['current_hardware']
        future_hw = config_data['hardware_settings']['future_hardware']
        
        print("\n🔧 Update Hardware Information:")
        
        # Current hardware
        new_current_name = input(f"Current hardware name [{current_hw['name']}]: ").strip()
        if new_current_name:
            current_hw['name'] = new_current_name
            
        new_current_desc = input(f"Current hardware description [{current_hw['description']}]: ").strip()
        if new_current_desc:
            current_hw['description'] = new_current_desc
        
        # Future hardware
        new_future_name = input(f"Future hardware name [{future_hw['name']}]: ").strip()
        if new_future_name:
            future_hw['name'] = new_future_name
            
        new_future_desc = input(f"Future hardware description [{future_hw['description']}]: ").strip()
        if new_future_desc:
            future_hw['description'] = new_future_desc
        
        return self._save_config(config_data, config_path)
    
    def _update_calculation_settings(self, config_data: Dict, config_path: str) -> bool:
        """Update calculation and correlation settings."""
        calc_settings = config_data['calculation_settings']
        
        print("\n🧮 Update Calculation Settings:")
        print("Current enabled approaches:", calc_settings['enabled_approaches'])
        
        # Update enabled approaches
        print("\nAvailable approaches:")
        print("1. hardware_calibrated")
        print("2. pure_simulation") 
        print("3. hybrid_correlation")
        
        approaches_input = input("Enter approach numbers to enable (e.g., '1,3') or press Enter to keep current: ").strip()
        if approaches_input:
            try:
                approach_map = {
                    '1': 'hardware_calibrated',
                    '2': 'pure_simulation',
                    '3': 'hybrid_correlation'
                }
                selected_nums = approaches_input.split(',')
                new_approaches = [approach_map[num.strip()] for num in selected_nums if num.strip() in approach_map]
                if new_approaches:
                    calc_settings['enabled_approaches'] = new_approaches
            except Exception:
                print("❌ Invalid approach selection!")
                return False
        
        # Update correlation factor
        current_corr = calc_settings['simulation_correlation']['correlation_factor']
        new_corr = input(f"Simulation correlation factor [{current_corr:.2e}]: ").strip()
        if new_corr:
            try:
                calc_settings['simulation_correlation']['correlation_factor'] = float(new_corr)
            except ValueError:
                print("❌ Invalid correlation factor!")
                return False
        
        return self._save_config(config_data, config_path)
    
    def _guided_full_update(self, config_data: Dict, config_path: str) -> bool:
        """Guided update of all configuration sections."""
        print("\n🎯 Guided Full Configuration Update")
        print("=" * 40)
        
        # Update each section in sequence
        sections = [
            ("Baseline Measurements", lambda: self._update_baseline_measurements(config_data, config_path)),
            ("Hardware Information", lambda: self._update_hardware_info(config_data, config_path)),
            ("Improvement Factors", lambda: self._update_improvement_factors(config_data, config_path)),
            ("Calculation Settings", lambda: self._update_calculation_settings(config_data, config_path))
        ]
        
        for section_name, update_func in sections:
            print(f"\n📋 {section_name}:")
            proceed = input(f"Update {section_name}? (y/n) [y]: ").strip().lower()
            if proceed in ['', 'y', 'yes']:
                # For guided update, we don't save after each step
                if section_name == "Baseline Measurements":
                    self._update_baseline_measurements(config_data, None)
                elif section_name == "Hardware Information":
                    self._update_hardware_info(config_data, None)
                elif section_name == "Improvement Factors":
                    self._update_improvement_factors(config_data, None)
                elif section_name == "Calculation Settings":
                    self._update_calculation_settings(config_data, None)
        
        # Save once at the end
        return self._save_config(config_data, config_path)
    
    def _save_config(self, config_data: Dict, config_path: str) -> bool:
        """Save configuration data to file."""
        if config_path is None:
            return True  # For guided updates, don't save until the end
            
        try:
            # Update metadata
            if 'metadata' not in config_data:
                config_data['metadata'] = {}
            config_data['metadata']['last_updated'] = datetime.now().isoformat()
            
            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            print(f"✅ Configuration updated: {config_path}")
            return True
        except Exception as e:
            print(f"❌ Error saving configuration: {e}")
            return False