#!/usr/bin/env python3
"""
Example usage scenarios for the flexible configuration system.
Demonstrates different ways to set up and use data sources.
"""

from config_manager import config, add_custom_csv_location, set_csv_directory, get_csv_path
import os

def example_1_check_current_setup():
    """Example 1: Check current configuration and available sources."""
    print("=" * 60)
    print("📊 EXAMPLE 1: Current Setup Status")
    print("=" * 60)
    
    print("Checking current configuration...")
    config.print_status_report()
    
    print("\nTesting CSV path resolution:")
    for freq in ["600MHz", "1000MHz", "1600MHz", "2000MHz"]:
        path = get_csv_path(freq)
        status = "✅ Available" if path else "❌ Not found"
        print(f"  {freq}: {status}")
        if path:
            print(f"    Path: {path}")

def example_2_add_custom_locations():
    """Example 2: Add custom CSV file locations."""
    print("\n" + "=" * 60)
    print("🔧 EXAMPLE 2: Adding Custom Locations")
    print("=" * 60)
    
    # Example custom paths (these are just examples)
    custom_examples = {
        "600MHz": r"C:\MyData\Simulations\600mhz_results.csv",
        "1000MHz": r"D:\Research\1000MHz_simulation_data.csv",
    }
    
    print("Adding custom file locations...")
    for freq, path in custom_examples.items():
        print(f"Adding {freq}: {path}")
        add_custom_csv_location(freq, path)
        # Note: These files don't actually exist, just for demonstration
    
    print("\nCustom paths added! Check status:")
    config.print_status_report()

def example_3_local_directory_setup():
    """Example 3: Set up a local CSV directory."""
    print("\n" + "=" * 60)
    print("📁 EXAMPLE 3: Local Directory Setup")
    print("=" * 60)
    
    # Example of organizing CSV files in a local directory
    local_dir = "my_simulation_data"
    
    print(f"Setting local CSV directory to: {local_dir}")
    set_csv_directory(local_dir)
    
    print("Expected file organization:")
    print(f"  {local_dir}/")
    print("  ├── simulation_results_600MHz.csv")
    print("  ├── simulation_results_1000MHz.csv")
    print("  ├── simulation_results_1600MHz.csv")
    print("  └── simulation_results_2000MHz.csv")
    
    print(f"\nTo use this setup:")
    print(f"1. Create directory: {local_dir}")
    print("2. Copy your CSV files with the expected names")
    print("3. Run: python universal_analyzer.py")

def example_4_mixed_sources():
    """Example 4: Using mixed data sources."""
    print("\n" + "=" * 60)
    print("🌐 EXAMPLE 4: Mixed Data Sources")
    print("=" * 60)
    
    print("In this scenario:")
    print("- 600MHz: Custom network location")
    print("- 1000MHz: Local CSV file")
    print("- 1600MHz: ZIP archive (default)")
    print("- 2000MHz: Network path (default)")
    
    # Add mixed sources
    add_custom_csv_location("600MHz", r"\\custom-server\share\600mhz_data.csv")
    add_custom_csv_location("1000MHz", r"C:\LocalData\1000MHz_results.csv")
    
    print("\nWith this setup, the analyzer will:")
    print("1. Use custom network path for 600MHz")
    print("2. Use local file for 1000MHz")
    print("3. Auto-extract ZIP for 1600MHz")
    print("4. Use default network path for 2000MHz")

def example_5_environment_migration():
    """Example 5: Easy environment migration."""
    print("\n" + "=" * 60)
    print("🚀 EXAMPLE 5: Environment Migration")
    print("=" * 60)
    
    print("Migration scenarios handled automatically:")
    print()
    
    print("🏢 Development Environment:")
    print("  - Network paths available")
    print("  - Uses: \\\\samba.zsc3.intel.com\\...")
    print("  - Command: python universal_analyzer.py")
    print()
    
    print("💻 Home/Offline Environment:")
    print("  - No network access")
    print("  - Uses: ZIP archives (automatic extraction)")
    print("  - Command: python universal_analyzer.py (same!)")
    print()
    
    print("☁️ Cloud/Remote Environment:")
    print("  - Custom data locations")
    print("  - Uses: Local directory or custom paths")
    print("  - Setup: python -c \"from config_manager import set_csv_directory; set_csv_directory('/data/csv')\"")
    print("  - Command: python universal_analyzer.py (same!)")
    print()
    
    print("🤝 Team Collaboration:")
    print("  - Each member has different data locations")
    print("  - Each runs setup once for their environment")
    print("  - Same analysis code works for everyone")

def example_6_troubleshooting():
    """Example 6: Common troubleshooting scenarios."""
    print("\n" + "=" * 60)
    print("🔍 EXAMPLE 6: Troubleshooting Guide")
    print("=" * 60)
    
    print("Problem: No data sources found")
    print("Solution: python config_manager.py  # Check status")
    print("          Add sources using examples above")
    print()
    
    print("Problem: Network paths not accessible")
    print("Solution: Automatic fallback to ZIP archives")
    print("          Or add local paths manually")
    print()
    
    print("Problem: ZIP files missing")
    print("Solution: python archive_csv_files.py  # Create from network")
    print("          Or copy CSV files to local directory")
    print()
    
    print("Problem: Custom paths not working")
    print("Solution: Check file permissions and paths")
    print("          Use absolute paths")
    print("          Verify files exist")
    print()
    
    print("Problem: Want to reset configuration")
    print("Solution: rm config.json")
    print("          python config_manager.py  # Creates new default")

def main():
    """Run all examples."""
    print("🎯 CONFIGURATION SYSTEM USAGE EXAMPLES")
    print("=" * 60)
    print("This demonstrates various ways to configure data sources")
    print("for different environments and use cases.")
    print()
    
    # Run examples
    example_1_check_current_setup()
    example_2_add_custom_locations()
    example_3_local_directory_setup()
    example_4_mixed_sources()
    example_5_environment_migration()
    example_6_troubleshooting()
    
    print("\n" + "=" * 60)
    print("✅ EXAMPLES COMPLETE")
    print("=" * 60)
    print("Next steps:")
    print("1. Check current status: python config_manager.py")
    print("2. Add your data sources using the examples above")
    print("3. Run analysis: python universal_analyzer.py")
    print("4. See CONFIG_README.md for detailed documentation")

if __name__ == "__main__":
    main()