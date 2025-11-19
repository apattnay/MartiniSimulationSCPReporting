#!/usr/bin/env python3
"""
Interactive Hardware Projection Tool - User Configuration Interface
Allows users to configure and execute hardware projections with different approaches.
"""

import json
import os
from pathlib import Path
from typing import List, Dict
import argparse
import sys
import pandas as pd

# Import our enhanced projector
from enhanced_hardware_projector import EnhancedHardwareProjector, CalculationApproach, HardwareProjectionConfig
from hardware_config_manager import HardwareConfigManager

class InteractiveProjectionTool:
    """Interactive tool for configurable hardware projections."""
    
    def __init__(self):
        self.config_file = "hardware_projection_config.json"
        self.projector = None
        
    def display_menu(self):
        """Display main menu options."""
        print("\n" + "="*60)
        print("🚀 Interactive Hardware Projection Tool v2.1")
        print("="*60)
        print("1. Run All Configured Approaches")
        print("2. Run Single Approach") 
        print("3. Hardware Configuration Manager (Create/Update/Browse)")
        print("4. Configure Calculation Settings")
        print("5. View Current Configuration")
        print("6. Load/Browse Configurations")
        print("7. Save Configuration to File")
        print("8. Run with Custom Scenario (Conservative/Optimistic)")
        print("9. Exit")
        print("-"*60)
        print(f"Current Config: {os.path.basename(self.config_file) if self.config_file else 'Default'}")
        print("-"*60)
    
    def get_user_choice(self, prompt: str, options: List[str]) -> str:
        """Get user choice with validation."""
        while True:
            choice = input(f"{prompt} ({'/'.join(options)}): ").strip().lower()
            if choice in [opt.lower() for opt in options]:
                return choice
            print(f"❌ Invalid choice. Please select from: {', '.join(options)}")
    
    def configure_approaches(self):
        """Allow user to configure which calculation approaches to run."""
        print("\n📊 Configure Calculation Approaches")
        print("-" * 40)
        print("Available Approaches:")
        print("1. Hardware-Calibrated: Uses hardware measurements + frequency scaling")  
        print("2. Pure Simulation: Uses simulation duration data directly")
        print("3. Hybrid Correlation: Combines hardware and simulation data")
        print("4. All Approaches: Run all three for comparison")
        
        choice = self.get_user_choice("Select approach", ["1", "2", "3", "4", "all"])
        
        if choice == "1":
            return [CalculationApproach.HARDWARE_CALIBRATED]
        elif choice == "2":
            return [CalculationApproach.PURE_SIMULATION] 
        elif choice == "3":
            return [CalculationApproach.HYBRID_CORRELATION]
        else:  # "4" or "all"
            return [CalculationApproach.HARDWARE_CALIBRATED, 
                   CalculationApproach.PURE_SIMULATION,
                   CalculationApproach.HYBRID_CORRELATION]
    
    def configure_hardware_parameters(self):
        """Enhanced hardware configuration with browser and creation capabilities."""
        print("\n🔧 Hardware Configuration Manager")
        print("-" * 40)
        
        hw_config_mgr = HardwareConfigManager()
        
        print("Hardware Configuration Options:")
        print("1. Browse and select existing configurations")
        print("2. Create new hardware configuration")
        print("3. Update existing configuration")
        print("4. Quick update current configuration")
        print("5. Return to main menu")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == '1':
            # Browse configurations
            selected_config = hw_config_mgr.display_config_browser()
            if selected_config:
                self.config_file = selected_config
                print(f"\n✅ Configuration loaded: {os.path.basename(selected_config)}")
            
        elif choice == '2':
            # Create new configuration
            new_config = hw_config_mgr.create_new_hardware_config()
            if new_config:
                self.config_file = new_config
                print(f"\n✅ New configuration created and loaded: {os.path.basename(new_config)}")
        
        elif choice == '3':
            # Update existing configuration
            configs = hw_config_mgr.list_available_configs()
            if configs:
                selected_config = hw_config_mgr.select_config_for_update(configs)
                if selected_config:
                    self.config_file = selected_config
            else:
                print("❌ No configurations available to update")
        
        elif choice == '4':
            # Quick update current configuration
            if self.config_file and os.path.exists(self.config_file):
                updated = hw_config_mgr.update_existing_config(self.config_file)
                if updated:
                    print("\n✅ Configuration updated successfully!")
                else:
                    print("\n❌ Configuration update cancelled or failed")
            else:
                print("❌ No current configuration file to update")
        
        elif choice == '5':
            return
        
        else:
            print("❌ Invalid choice")
        
    def run_single_approach(self):
        """Run a single user-selected approach."""
        print("\n🎯 Run Single Approach")
        print("-" * 30)
        
        approaches = self.configure_approaches() 
        if len(approaches) > 1:
            print("⚠️ Multiple approaches selected. Running first one only.")
            approaches = [approaches[0]]
        
        self.execute_projection(approaches)
    
    def run_all_approaches(self):
        """Run all configured approaches."""
        print("\n🚀 Running All Configured Approaches")
        print("-" * 40)
        
        approaches = [
            CalculationApproach.HARDWARE_CALIBRATED,
            CalculationApproach.PURE_SIMULATION, 
            CalculationApproach.HYBRID_CORRELATION
        ]
        
        self.execute_projection(approaches)
    
    def run_custom_scenario(self):
        """Run with custom conservative/optimistic scenarios."""
        print("\n🎭 Custom Scenario Analysis")
        print("-" * 30)
        print("1. Conservative Estimates")
        print("2. Optimistic Estimates") 
        print("3. Current Configuration")
        
        choice = self.get_user_choice("Select scenario", ["1", "2", "3"])
        
        # Load base config
        config_mgr = HardwareProjectionConfig(self.config_file)
        
        if choice == "1":
            print("📉 Running Conservative Scenario...")
            # Apply conservative estimates
            alt_config = config_mgr.config['alternative_hardware_scenarios']['conservative_estimates']
            self.apply_scenario_config(config_mgr, alt_config)
        elif choice == "2":  
            print("📈 Running Optimistic Scenario...")
            # Apply optimistic estimates
            alt_config = config_mgr.config['alternative_hardware_scenarios']['optimistic_estimates']
            self.apply_scenario_config(config_mgr, alt_config)
        else:
            print("📊 Running Current Configuration...")
        
        # Create projector with modified config
        projector = EnhancedHardwareProjector()
        if choice != "3":
            projector.config = config_mgr.config
            projector.improvement_factors = config_mgr.config['hardware_settings']['future_hardware']['improvement_factors']
        
        # Run all approaches for scenario comparison
        approaches = [CalculationApproach.HARDWARE_CALIBRATED,
                     CalculationApproach.PURE_SIMULATION,
                     CalculationApproach.HYBRID_CORRELATION]
        
        projections_df = projector.calculate_projections(approaches)
        self.display_results(projections_df, scenario=choice)
    
    def apply_scenario_config(self, config_mgr: HardwareProjectionConfig, alt_config: Dict):
        """Apply alternative scenario configuration."""
        improvements = config_mgr.config['hardware_settings']['future_hardware']['improvement_factors']
        
        # Update improvement factors with scenario values
        improvements['xecore_compute']['value'] = alt_config['xecore_compute']
        improvements['hbm_bandwidth']['value'] = alt_config['hbm_bandwidth']  
        improvements['fabrication_process']['value'] = alt_config['fabrication_process']
        improvements['communication']['bandwidth_improvement']['value'] = alt_config['communication_bandwidth']
        improvements['communication']['latency_improvement']['value'] = alt_config['communication_latency']
    
    def execute_projection(self, approaches: List[CalculationApproach]):
        """Execute projection calculations with specified approaches."""
        print(f"\n🔄 Executing projections with {len(approaches)} approach(es)...")
        
        # Initialize projector
        projector = EnhancedHardwareProjector(self.config_file)
        
        # Calculate projections
        projections_df = projector.calculate_projections(approaches)
        
        # Display and export results
        self.display_results(projections_df)
        
        # Generate analysis
        analysis = projector.generate_comparison_analysis(projections_df)
        
        # Export results
        projector.export_results(projections_df, analysis)
        
    def display_results(self, projections_df, scenario: str = None):
        """Display projection results in a user-friendly format."""
        if projections_df.empty:
            print("❌ No results to display. Check input data and configuration.")
            return
        
        scenario_label = ""
        if scenario == "1":
            scenario_label = " (Conservative)"
        elif scenario == "2":
            scenario_label = " (Optimistic)"
        elif scenario == "3":
            scenario_label = " (Current Config)"
        
        print(f"\n📈 Projection Results{scenario_label}")
        print("=" * (25 + len(scenario_label)))
        
        # Display current hardware baseline first
        baseline_cols = {
            'hw_calibrated_baseline_tgs': 'Hardware-Calibrated Baseline',
            'pure_sim_current_tgs': 'Pure Simulation Current',
            'hybrid_baseline_tgs': 'Hybrid Baseline'
        }
        
        print("\n📊 Current Hardware Performance (Reference):")
        print("-" * 45)
        baseline_found = False
        
        # Show individual frequency values instead of summary
        for col_name, display_name in baseline_cols.items():
            if col_name in projections_df.columns:
                # Display frequency-by-frequency baseline values
                freq_values = []
                for _, row in projections_df.iterrows():
                    if col_name in row and not pd.isna(row[col_name]):
                        freq_str = row['frequency_str']
                        baseline_val = row[col_name]
                        freq_values.append((freq_str, baseline_val))
                
                if freq_values:
                    print(f"  {display_name}:")
                    for freq_str, val in freq_values:
                        print(f"    {freq_str:8}: {val:8.2f} tok/s")
                    baseline_found = True
                    break
        
        if not baseline_found:
            print("  Baseline data not available")
        
        # Display projected results
        print(f"\n🚀 Projected Hardware Performance:")
        print("-" * 35)
        
        approaches_cols = {
            'Hardware-Calibrated': 'hw_calibrated_improved_tgs',
            'Pure Simulation': 'pure_sim_improved_tgs', 
            'Hybrid Correlation': 'hybrid_improved_tgs'
        }
        
        results_table = []
        
        for approach_name, col_name in approaches_cols.items():
            if col_name in projections_df.columns:
                values = projections_df[col_name].dropna()
                if len(values) > 0:
                    results_table.append({
                        'Approach': approach_name,
                        'Min TGS': f"{values.min():.2f}",
                        'Max TGS': f"{values.max():.2f}", 
                        'Avg TGS': f"{values.mean():.2f}",
                        'Range': f"{values.max() - values.min():.2f}"
                    })
        
        if results_table:
            # Print table header
            print(f"{'Approach':<20} {'Min TGS':<10} {'Max TGS':<10} {'Avg TGS':<10} {'Range':<10}")
            print("-" * 70)
            
            # Print table rows
            for row in results_table:
                print(f"{row['Approach']:<20} {row['Min TGS']:<10} {row['Max TGS']:<10} {row['Avg TGS']:<10} {row['Range']:<10}")
        
        # Display frequency breakdown
        print(f"\n📊 Detailed Results by Frequency:")
        print("-" * 50)
        for _, row in projections_df.iterrows():
            freq = row['frequency_str']
            print(f"\n{freq}:")
            
            for approach_name, col_name in approaches_cols.items():
                if col_name in row and not pd.isna(row[col_name]):
                    print(f"  {approach_name:18}: {row[col_name]:8.2f} tok/s")
    
    def view_configuration(self):
        """Display current configuration."""
        print("\n📋 Current Configuration")
        print("-" * 30)
        
        try:
            config_mgr = HardwareProjectionConfig(self.config_file)
            config = config_mgr.config
            
            # Hardware settings
            hw = config['hardware_settings']
            print(f"Current Hardware: {hw['current_hardware']['name']} - {hw['current_hardware']['description']}")
            print(f"Future Hardware:  {hw['future_hardware']['name']} - {hw['future_hardware']['description']}")
            
            # Improvement factors
            improvements = hw['future_hardware']['improvement_factors']
            print(f"\nImprovement Factors:")
            print(f"  XeCore Compute:      {improvements['xecore_compute']['value']:.3f}")
            print(f"  HBM Bandwidth:       {improvements['hbm_bandwidth']['value']:.1f}x")
            print(f"  Fabrication Process: {improvements['fabrication_process']['value']:.3f}")
            print(f"  Comm Bandwidth:      {improvements['communication']['bandwidth_improvement']['value']:.1f}x")
            print(f"  Comm Latency:        {improvements['communication']['latency_improvement']['value']:.0f}x")
            
            # Calculation settings
            calc = config['calculation_settings']
            print(f"\nCalculation Settings:")
            print(f"  Enabled Approaches: {calc['enabled_approaches']}")
            print(f"  Correlation Factor: {calc['simulation_correlation']['correlation_factor']:.2e}")
            
        except Exception as e:
            print(f"❌ Error loading configuration: {e}")
    
    def load_configuration(self):
        """Load configuration from file with browser interface."""
        print("\n📁 Load Configuration")
        print("-" * 30)
        
        hw_config_mgr = HardwareConfigManager()
        
        print("Load Configuration Options:")
        print("1. Browse available configurations")
        print("2. Enter specific file path")
        print("3. Return to main menu")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == '1':
            # Use configuration browser
            selected_config = hw_config_mgr.display_config_browser()
            if selected_config:
                self.config_file = selected_config
                try:
                    config_mgr = HardwareProjectionConfig(selected_config)
                    hw_config = config_mgr.config['hardware_settings']
                    print(f"\n✅ Configuration loaded successfully!")
                    print(f"Hardware: {hw_config['current_hardware']['name']} → {hw_config['future_hardware']['name']}")
                except Exception as e:
                    print(f"❌ Error loading configuration: {e}")
        
        elif choice == '2':
            # Manual file path entry
            filename = input("Enter configuration filename (or press Enter for default): ").strip()
            if not filename:
                filename = self.config_file
                
            if Path(filename).exists():
                try:
                    config_mgr = HardwareProjectionConfig(filename)
                    self.config_file = filename
                    hw_config = config_mgr.config['hardware_settings']
                    print(f"\n✅ Configuration loaded from {filename}")
                    print(f"Hardware: {hw_config['current_hardware']['name']} → {hw_config['future_hardware']['name']}")
                except Exception as e:
                    print(f"❌ Error loading configuration: {e}")
            else:
                print(f"❌ File {filename} not found.")
        
        elif choice == '3':
            return
        
        else:
            print("❌ Invalid choice")
    
    def save_configuration(self):
        """Save current configuration to user-specified file."""
        print("\n💾 Save Configuration")
        print("-" * 25)
        
        filename = input("Enter filename to save (or press Enter for default): ").strip()
        if not filename:
            filename = self.config_file
        
        try:
            config_mgr = HardwareProjectionConfig(self.config_file)
            config_mgr.save_config(filename)
            print(f"✅ Configuration saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving configuration: {e}")
    
    def run(self):
        """Main interactive loop."""
        while True:
            self.display_menu()
            choice = input("Enter your choice (1-9): ").strip()
            
            if choice == "1":
                self.run_all_approaches()
            elif choice == "2": 
                self.run_single_approach()
            elif choice == "3":
                self.configure_hardware_parameters()
            elif choice == "4":
                print("📊 Calculation settings configuration coming soon!")
            elif choice == "5":
                self.view_configuration()
            elif choice == "6":
                self.load_configuration()
            elif choice == "7":
                self.save_configuration()
            elif choice == "8":
                self.run_custom_scenario()
            elif choice == "9":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please select 1-9.")
            
            # Pause for user to read results
            if choice in ["1", "2", "8"]:
                input("\n📍 Press Enter to continue...")

def main():
    """Main entry point with command line argument support."""
    parser = argparse.ArgumentParser(description="Interactive Hardware Projection Tool")
    parser.add_argument("--config", "-c", help="Configuration file path", default="hardware_projection_config.json")
    parser.add_argument("--approach", "-a", choices=["hw", "sim", "hybrid", "all"], 
                       help="Run specific approach directly (hw=hardware-calibrated, sim=pure-simulation, hybrid=hybrid-correlation, all=all approaches)")
    parser.add_argument("--scenario", "-s", choices=["conservative", "optimistic", "current"],
                       help="Run with predefined scenario")
    parser.add_argument("--interactive", "-i", action="store_true", default=True,
                       help="Run in interactive mode (default)")
    
    args = parser.parse_args()
    
    # Create interactive tool
    tool = InteractiveProjectionTool()
    tool.config_file = args.config
    
    # Handle command line execution
    if args.approach and not args.interactive:
        print(f"🚀 Running {args.approach} approach directly...")
        
        # Map approach names
        approach_map = {
            "hw": [CalculationApproach.HARDWARE_CALIBRATED],
            "sim": [CalculationApproach.PURE_SIMULATION], 
            "hybrid": [CalculationApproach.HYBRID_CORRELATION],
            "all": [CalculationApproach.HARDWARE_CALIBRATED, 
                   CalculationApproach.PURE_SIMULATION,
                   CalculationApproach.HYBRID_CORRELATION]
        }
        
        tool.execute_projection(approach_map[args.approach])
        
    elif args.scenario and not args.interactive:
        print(f"🎭 Running {args.scenario} scenario...")
        # Set scenario choice and run
        choice_map = {"conservative": "1", "optimistic": "2", "current": "3"}
        # This would need the scenario logic extracted to be callable directly
        print("💡 Use interactive mode for scenario analysis: python interactive_projector.py -i")
        
    else:
        # Run interactive mode
        tool.run()

if __name__ == "__main__":
    # Fix import issue for standalone execution
    import pandas as pd
    main()