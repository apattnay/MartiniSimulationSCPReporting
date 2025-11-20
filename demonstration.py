#!/usr/bin/env python3
"""
Demonstration Script - Hardware Projection System
Shows the key features of the enhanced configuration management system.
"""

import os
import sys
from pathlib import Path

# Import our modules
try:
    from hardware_config_manager import HardwareConfigManager
    from enhanced_hardware_projector import EnhancedHardwareProjector, CalculationApproach
    from interactive_projector import InteractiveProjectionTool
    print("✅ All modules imported successfully!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def demonstrate_config_manager():
    """Demonstrate the hardware configuration manager features."""
    print("\n" + "="*60)
    print("🔧 Hardware Configuration Manager Demo")
    print("="*60)
    
    config_mgr = HardwareConfigManager()
    
    # Show available configurations
    print("\n📁 Available Configurations:")
    configs = config_mgr.list_available_configs()
    print(f"Found {len(configs)} configuration(s)")
    
    for i, config_dict in enumerate(configs, 1):
        config_name = config_dict['name']
        config_desc = config_dict['description']
        print(f"  {i}. {config_name}: {config_desc}")
    
    # Show configuration browser (non-interactive demo)
    print(f"\n🌐 Configuration Browser Features:")
    print(f"  • Browse and select configurations")
    print(f"  • View configuration metadata")
    print(f"  • Create new configurations with validation")
    print(f"  • Update existing configurations")
    print(f"  • Prevent division by zero with input validation")
    
    return True

def demonstrate_enhanced_projector():
    """Demonstrate the enhanced projector features."""
    print("\n" + "="*60)
    print("🚀 Enhanced Hardware Projector Demo")
    print("="*60)
    
    try:
        # Load default configuration
        config_file = "hardware_projection_config.json"
        if not os.path.exists(config_file):
            print(f"❌ Default config file not found: {config_file}")
            return False
            
        projector = EnhancedHardwareProjector(config_file)
        print(f"✅ Enhanced projector loaded with: {config_file}")
        
        # Show configuration details
        print(f"\n📊 Configuration Details:")
        hw_config = projector.config['hardware_settings']
        current_hw = hw_config['current_hardware']
        future_hw = hw_config['future_hardware']
        
        print(f"  Current Hardware: {current_hw['name']} - {current_hw['description']}")
        print(f"  Future Hardware:  {future_hw['name']} - {future_hw['description']}")
        
        print(f"\n📈 Key Improvement Factors:")
        improvements = future_hw['improvement_factors']
        print(f"  • XeCore Compute:      {improvements['xecore_compute']['value']:.3f}")
        print(f"  • HBM Bandwidth:       {improvements['hbm_bandwidth']['value']:.1f}x")
        print(f"  • Fabrication Process: {improvements['fabrication_process']['value']:.3f}")
        print(f"  • Comm Bandwidth:      {improvements['communication']['bandwidth_improvement']['value']:.1f}x")
        print(f"  • Comm Latency:        {improvements['communication']['latency_improvement']['value']:.0f}x")
        
        print(f"\n🎯 Available Calculation Approaches:")
        print(f"  1. Hardware-Calibrated: Uses actual hardware measurements as baseline")
        print(f"  2. Pure Simulation:     Uses simulation data exclusively")
        print(f"  3. Hybrid Correlation:  Combines both approaches for comprehensive analysis")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced projector demo failed: {e}")
        return False

def demonstrate_interactive_features():
    """Demonstrate the interactive projector features."""
    print("\n" + "="*60)
    print("🎮 Interactive Projector Features")
    print("="*60)
    
    try:
        tool = InteractiveProjectionTool()
        print(f"✅ Interactive tool initialized")
        
        print(f"\n🎯 Key Interactive Features:")
        print(f"  • Menu-driven interface with 9 main options")
        print(f"  • Configuration browser with metadata display")
        print(f"  • Step-by-step configuration creation wizard")
        print(f"  • Real-time configuration updates")
        print(f"  • Multiple execution approaches (single or all)")
        print(f"  • Custom scenario analysis (conservative/optimistic)")
        print(f"  • Detailed frequency analysis tables")
        print(f"  • Performance visualization plots")
        print(f"  • Current hardware TGS reference display")
        
        print(f"\n🔧 Configuration Management:")
        print(f"  • Create new hardware configurations")
        print(f"  • Browse existing configurations with metadata")
        print(f"  • Update improvement factors with validation")
        print(f"  • Load configurations by browsing or file path")
        print(f"  • Save configurations to custom files")
        
        return True
        
    except Exception as e:
        print(f"❌ Interactive features demo failed: {e}")
        return False

def show_usage_examples():
    """Show usage examples for the system."""
    print("\n" + "="*60)
    print("💡 Usage Examples")
    print("="*60)
    
    print(f"\n🚀 Quick Start:")
    print(f"  1. Start interactive tool:  python interactive_projector.py")
    print(f"  2. Choose option 1:        Run All Configured Approaches")
    print(f"  3. Review results:         Current vs projected performance")
    
    print(f"\n🔧 Configuration Management:")
    print(f"  1. Start interactive tool:  python interactive_projector.py")
    print(f"  2. Choose option 3:        Hardware Configuration Manager")
    print(f"  3. Select option 2:        Create new hardware configuration")
    print(f"  4. Follow the wizard:      Enter hardware specifications")
    
    print(f"\n📊 Analysis Workflow:")
    print(f"  1. Create/load config:     Define hardware improvements")
    print(f"  2. Run projections:        Execute all calculation approaches")
    print(f"  3. Review results:         Frequency tables, plots, analysis")
    print(f"  4. Export data:            CSV/JSON reports for further analysis")
    
    print(f"\n🎭 Scenario Comparison:")
    print(f"  1. Start with option 8:    Run with Custom Scenario")
    print(f"  2. Compare scenarios:      Conservative vs Optimistic vs Current")
    print(f"  3. Analyze differences:    Side-by-side performance comparison")

def main():
    """Run the demonstration."""
    print("🚀 Hardware Projection System - Feature Demonstration")
    print("=" * 65)
    
    # Run demonstrations
    demos = [
        ("Configuration Manager", demonstrate_config_manager),
        ("Enhanced Projector", demonstrate_enhanced_projector),
        ("Interactive Features", demonstrate_interactive_features)
    ]
    
    results = []
    for demo_name, demo_func in demos:
        print(f"\n🎯 Running {demo_name} Demo...")
        results.append(demo_func())
    
    # Show usage examples
    show_usage_examples()
    
    # Summary
    print(f"\n📋 Demo Summary")
    print("-" * 20)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All demonstrations completed successfully! ({passed}/{total})")
        print(f"\n✅ System Status: Ready for use")
        print(f"🔧 Error Resolution: Division by zero validation implemented")
        print(f"📈 New Features: Enhanced configuration management system")
    else:
        print(f"⚠️  Some demonstrations had issues ({passed}/{total})")
    
    print(f"\n🚀 To start using the system:")
    print(f"   python interactive_projector.py")
    
    print(f"\n🧪 To test system integration:")
    print(f"   python test_integration.py")

if __name__ == "__main__":
    main()