#!/usr/bin/env python3
"""
Universal Auto-Analyzer - Smart data source detection and analysis
Supports multiple data source types with automatic fallback and configuration.
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path
from config_manager import config, get_csv_path

def analyze_single_frequency(freq_name: str) -> dict:
    """Analyze a single frequency sweep using smart path detection."""
    print(f"\n{'='*60}")
    print(f"Analyzing {freq_name}")
    print(f"{'='*60}")
    
    # Get CSV file using configuration manager
    csv_file = get_csv_path(freq_name)
    
    if not csv_file:
        print(f"❌ No CSV file available for {freq_name}")
        return None
    
    print(f"📁 Using CSV file: {csv_file}")
    try:
        # Load CSV
        df = pd.read_csv(csv_file)
        print(f"✅ Loaded {len(df):,} rows, {len(df.columns)} columns")
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return None
    
    # Validate required columns
    required_cols = ['RESOURCE', 'DURATION', 'TRANSITION']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        print(f"⚠️ Missing required columns: {missing_cols}")
        print(f"Available columns: {df.columns.tolist()}")
        return None
    
    # Filter for GT resources
    print("🔍 Filtering for gt/* resources...")
    gt_mask = df['RESOURCE'].str.startswith('gt/', na=False)
    gt_df = df[gt_mask].copy()
    print(f"✅ Found {len(gt_df):,} GT resources ({len(gt_df)/len(df)*100:.1f}% of total)")
    
    if len(gt_df) == 0:
        print("⚠️ No GT resources found!")
        return None
    
    # Duration analysis
    print("📊 Analyzing durations...")
    gt_df['DURATION'] = pd.to_numeric(gt_df['DURATION'], errors='coerce')
    
    # Remove any invalid durations
    valid_durations = gt_df['DURATION'].notna()
    gt_df = gt_df[valid_durations]
    
    if len(gt_df) == 0:
        print("⚠️ No valid duration data found!")
        return None
    
    duration_stats = {
        'total_duration': gt_df['DURATION'].sum(),
        'avg_duration': gt_df['DURATION'].mean(),
        'median_duration': gt_df['DURATION'].median(),
        'max_duration': gt_df['DURATION'].max(),
        'min_duration': gt_df['DURATION'].min(),
        'std_duration': gt_df['DURATION'].std(),
        'count': len(gt_df)
    }
    
    print(f"💰 TOTAL DURATION: {duration_stats['total_duration']:,.6f}")
    print(f"📈 Average: {duration_stats['avg_duration']:.6f}")
    print(f"📊 Median: {duration_stats['median_duration']:.6f}")
    print(f"🔺 Max: {duration_stats['max_duration']:.6f}")
    print(f"🔻 Min: {duration_stats['min_duration']:.6f}")
    
    # Transition analysis
    print("🔄 Analyzing transitions...")
    transition_summary = gt_df.groupby('TRANSITION').agg({
        'DURATION': ['count', 'sum', 'mean', 'median']
    }).round(6)
    
    transition_summary.columns = ['count', 'total_duration', 'avg_duration', 'median_duration']
    transition_summary = transition_summary.reset_index()
    transition_summary = transition_summary.sort_values('total_duration', ascending=False)
    
    print(f"🎯 Found {len(transition_summary)} unique transitions")
    
    # Show top transitions
    print("\n🏆 TOP 10 TRANSITIONS BY TOTAL DURATION:")
    print("-" * 80)
    for i, (_, row) in enumerate(transition_summary.head(10).iterrows(), 1):
        print(f"{i:2d}. {row['total_duration']:12.6f} | {row['count']:6d} times | {row['TRANSITION'][:50]}...")
    
    # Save results
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    freq_clean = freq_name.replace('MHz', '').replace('/', '_')
    
    # Save transition summary
    trans_file = os.path.join(output_dir, f"{freq_clean}_transitions.xlsx")
    transition_summary.to_excel(trans_file, index=False)
    print(f"\n💾 Saved transition analysis: {trans_file}")
    
    # Determine data source type for reporting
    data_source = "Unknown"
    if csv_file.startswith('\\\\'):
        data_source = "Network"
    elif 'temp_data' in csv_file:
        data_source = "ZIP Archive"
    elif 'local_csv' in csv_file:
        data_source = "Local Directory"
    else:
        data_source = "Custom Path"
    
    # Save summary stats
    summary_data = {
        'Frequency': freq_name,
        'Total_Rows': len(df),
        'GT_Rows': len(gt_df),
        'GT_Percentage': len(gt_df)/len(df)*100,
        **duration_stats,
        'Unique_Transitions': len(transition_summary),
        'Data_Source': data_source,
        'File_Path': csv_file
    }
    
    return summary_data

def interactive_setup():
    """Interactive setup for adding custom data locations."""
    print("\n🔧 INTERACTIVE DATA SOURCE SETUP")
    print("=" * 50)
    
    print("This will help you configure data source locations.")
    print("Current configuration will be preserved.\n")
    
    # Show current status
    config.print_status_report()
    
    print("\n" + "="*50)
    print("SETUP OPTIONS:")
    print("1. Add custom CSV file location")
    print("2. Set local CSV directory") 
    print("3. Show current configuration")
    print("4. Test current configuration")
    print("5. Continue with analysis")
    
    while True:
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            freq = input("Enter frequency (600MHz/1000MHz/1600MHz/2000MHz): ").strip()
            if freq not in ["600MHz", "1000MHz", "1600MHz", "2000MHz"]:
                print("❌ Invalid frequency!")
                continue
            
            path = input("Enter full path to CSV file or directory: ").strip()
            if not path:
                print("❌ Path cannot be empty!")
                continue
            
            config.add_custom_path(freq, path)
            print(f"✅ Added custom location for {freq}")
        
        elif choice == "2":
            directory = input("Enter local CSV directory path: ").strip()
            if not directory:
                print("❌ Directory cannot be empty!")
                continue
            
            config.set_local_csv_directory(directory)
        
        elif choice == "3":
            config.print_status_report()
        
        elif choice == "4":
            print("\n🧪 Testing configuration...")
            for freq in ["600MHz", "1000MHz", "1600MHz", "2000MHz"]:
                csv_path = get_csv_path(freq)
                status = "✅ Found" if csv_path else "❌ Not found"
                print(f"   {freq}: {status}")
                if csv_path:
                    print(f"      Path: {csv_path}")
        
        elif choice == "5":
            break
        
        else:
            print("❌ Invalid choice! Please enter 1-5.")

def main():
    """Main analysis function with smart data source detection."""
    frequencies = ["600MHz", "1000MHz", "1600MHz", "2000MHz"]
    
    print("🚀 UNIVERSAL SIMULATION RESULTS ANALYZER")
    print("=" * 60)
    print("Smart data source detection with automatic fallback")
    print("Supports: Network paths, ZIP archives, local files, custom locations")
    
    # Check if we need interactive setup
    available_sources = 0
    for freq in frequencies:
        if get_csv_path(freq):
            available_sources += 1
    
    if available_sources == 0:
        print("\n⚠️ No data sources found with current configuration!")
        setup_choice = input("Would you like to configure data sources? (y/n): ").strip().lower()
        if setup_choice == 'y':
            interactive_setup()
        else:
            print("❌ Cannot proceed without data sources. Exiting.")
            return
    elif available_sources < len(frequencies):
        print(f"\n⚠️ Only {available_sources}/{len(frequencies)} frequencies have data sources.")
        print("Some analysis may be incomplete.")
        setup_choice = input("Configure additional sources? (y/n): ").strip().lower()
        if setup_choice == 'y':
            interactive_setup()
    
    # Run analysis
    print(f"\n📋 Starting analysis for {len(frequencies)} frequencies...")
    all_summaries = []
    
    for i, freq_name in enumerate(frequencies, 1):
        print(f"\n📋 Processing {i}/{len(frequencies)}: {freq_name}")
        try:
            summary = analyze_single_frequency(freq_name)
            if summary:
                all_summaries.append(summary)
                print(f"✅ {freq_name} completed successfully")
            else:
                print(f"❌ {freq_name} failed or no data available")
        except Exception as e:
            print(f"❌ Error processing {freq_name}: {e}")
    
    # Generate comprehensive summary
    if all_summaries:
        print("\n" + "="*100)
        print("📋 COMPREHENSIVE ANALYSIS SUMMARY")
        print("="*100)
        
        summary_df = pd.DataFrame(all_summaries)
        
        # Display summary with data sources
        print("\n🎯 ANALYSIS RESULTS BY FREQUENCY:")
        print("-" * 100)
        for _, row in summary_df.iterrows():
            source_icons = {
                "Network": "🌐",
                "ZIP Archive": "📦", 
                "Local Directory": "📁",
                "Custom Path": "🔧",
                "Unknown": "❓"
            }
            icon = source_icons.get(row['Data_Source'], "❓")
            
            print(f"{row['Frequency']:>8} {icon} | GT Resources: {row['GT_Rows']:>8,} | "
                  f"Total Duration: {row['total_duration']:>15,.2f} | Avg: {row['avg_duration']:>8.2f}")
            print(f"         Source: {row['Data_Source']} | Path: {row['File_Path'][:70]}...")
        
        # Save results
        os.makedirs("output", exist_ok=True)
        summary_df.to_excel("output/universal_analysis_summary.xlsx", index=False)
        summary_df.to_csv("output/universal_analysis_summary.csv", index=False)
        print(f"\n💾 Results saved to output/universal_analysis_summary.xlsx")
        
        # Calculate statistics
        total_gt_resources = summary_df['GT_Rows'].sum()
        total_effort = summary_df['total_duration'].sum()
        avg_effort_per_freq = summary_df['total_duration'].mean()
        
        print("\n" + "="*100)
        print("🎯 OVERALL ANALYSIS STATISTICS")
        print("="*100)
        print(f"📊 Total GT/* Resources: {total_gt_resources:,}")
        print(f"💰 Total Effort: {total_effort:,.2f}")
        print(f"📈 Average Effort Per Frequency: {avg_effort_per_freq:,.2f}")
        print(f"🔢 Frequencies Analyzed: {len(all_summaries)}")
        
        # Data source summary
        source_counts = summary_df['Data_Source'].value_counts()
        print(f"\n📊 Data Sources Used:")
        for source, count in source_counts.items():
            icon = {"Network": "🌐", "ZIP Archive": "📦", "Local Directory": "📁", "Custom Path": "🔧"}.get(source, "❓")
            print(f"   {icon} {source}: {count} frequencies")
        
        # Frequency comparison
        print("\n📈 EFFORT COMPARISON:")
        print("-" * 60)
        for _, row in summary_df.iterrows():
            percentage = (row['total_duration'] / total_effort) * 100
            print(f"{row['Frequency']:>8}: {row['total_duration']:>12,.2f} ({percentage:5.1f}%)")
        
        print("\n✅ Analysis Complete!")
        print("📁 Check 'output/' folder for detailed results")
        print("🔧 Use 'python config_manager.py' to manage data sources")
        
        # Cleanup if configured
        if config.config["analysis_settings"]["cleanup_extracted_files"]:
            cleanup_path = Path("temp_data")
            if cleanup_path.exists():
                import shutil
                shutil.rmtree(cleanup_path)
                print("🧹 Cleaned up extracted files")
    
    else:
        print("\n❌ No data was successfully analyzed!")
        print("\n💡 Troubleshooting steps:")
        print("1. Run: python config_manager.py  # Check data source status")
        print("2. Add data sources using interactive setup")
        print("3. Verify file paths and permissions")
        print("4. Check if ZIP files need extraction")

if __name__ == "__main__":
    main()