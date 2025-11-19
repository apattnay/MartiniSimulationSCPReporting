#!/usr/bin/env python3
"""
Test Integration Script
Tests the complete hardware projection system with configuration management.
"""

import os
import sys
from pathlib import Path

# Test imports
try:
    from hardware_config_manager import HardwareConfigManager
    from interactive_projector import InteractiveProjectionTool
    from enhanced_hardware_projector import EnhancedHardwareProjector, HardwareProjectionConfig
    print("✅ All imports successful!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_config_manager():
    """Test the hardware config manager functionality."""
    print("\n🧪 Testing Hardware Config Manager")
    print("-" * 40)
    
    try:
        # Initialize config manager
        config_mgr = HardwareConfigManager()
        
        # Test listing configs
        configs = config_mgr.list_available_configs()
        print(f"Available configs: {len(configs)} found")
        
        # Test config directory creation
        if Path(config_mgr.config_dir).exists():
            print(f"✅ Config directory exists: {config_mgr.config_dir}")
        else:
            print(f"📁 Config directory created: {config_mgr.config_dir}")
            
        return True
        
    except Exception as e:
        print(f"❌ Config manager test failed: {e}")
        return False

def test_interactive_projector():
    """Test the interactive projector initialization."""
    print("\n🧪 Testing Interactive Projector")
    print("-" * 40)
    
    try:
        # Initialize interactive tool
        tool = InteractiveProjectionTool()
        print(f"✅ Interactive tool initialized")
        print(f"   Default config: {tool.config_file}")
        
        # Check if default config exists
        if os.path.exists(tool.config_file):
            print(f"✅ Default configuration file found")
        else:
            print(f"⚠️  Default configuration file not found: {tool.config_file}")
            
        return True
        
    except Exception as e:
        print(f"❌ Interactive projector test failed: {e}")
        return False

def test_enhanced_projector():
    """Test the enhanced hardware projector."""
    print("\n🧪 Testing Enhanced Hardware Projector")
    print("-" * 40)
    
    try:
        # Check if config file exists, create minimal one if not
        config_file = "hardware_projection_config.json"
        if not os.path.exists(config_file):
            print(f"⚠️  Config file not found, cannot test enhanced projector")
            return False
            
        # Initialize enhanced projector
        projector = EnhancedHardwareProjector(config_file)
        print(f"✅ Enhanced projector initialized")
        
        # Test config loading
        config_mgr = HardwareProjectionConfig(config_file)
        print(f"✅ Configuration loaded successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced projector test failed: {e}")
        return False

def display_system_info():
    """Display system information."""
    print("\n📊 System Information")
    print("-" * 30)
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Script location: {Path(__file__).parent}")
    
    # Check for data files
    data_files = ["temp_data", "output", "data"]
    for data_dir in data_files:
        if os.path.exists(data_dir):
            print(f"✅ Directory found: {data_dir}")
        else:
            print(f"❌ Directory missing: {data_dir}")

def main():
    """Run integration tests."""
    print("🚀 Hardware Projection System - Integration Test")
    print("=" * 55)
    
    # Display system info
    display_system_info()
    
    # Run tests
    tests = [
        test_config_manager,
        test_interactive_projector,
        test_enhanced_projector
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    # Summary
    print("\n📋 Test Summary")
    print("-" * 20)
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! System ready for use.")
        print("\n💡 To start the interactive tool, run:")
        print("   python interactive_projector.py")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
        
    print(f"\n🔧 Available tools:")
    print(f"   • Interactive Projector: python interactive_projector.py")
    print(f"   • Direct Enhanced Projector: python enhanced_hardware_projector.py")
    print(f"   • Configuration Manager: Direct import in Python")

if __name__ == "__main__":
    main()