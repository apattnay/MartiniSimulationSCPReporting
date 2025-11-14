#!/usr/bin/env python3
"""
Quick analysis script - processes one frequency at a time for better control.
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path

def analyze_single_frequency(freq_name, path):
    """Analyze a single frequency sweep."""
    print(f"\n{'='*60}")
    print(f"Analyzing {freq_name}")
    print(f"Path: {path}")
    print(f"{'='*60}")
    
    csv_file = os.path.join(path, 'simulation_results.csv')
    
    if not os.path.exists(csv_file):
        print(f"❌ File not found: {csv_file}")
        return None
    
    print("📁 Loading CSV file...")
    try:
        # Load with progress indication
        df = pd.read_csv(csv_file)
        print(f"✅ Loaded {len(df):,} rows, {len(df.columns)} columns")
    except Exception as e:
        print(f"❌ Error loading file: {e}")
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
    print("\n🏆 TOP 10 TRANSITIONS BY TOTAL DURATION:")
    print("-" * 80)
    for i, row in transition_summary.head(10).iterrows():
        print(f"{i+1:2d}. {row['total_duration']:12.6f} | {row['count']:6d} times | {row['TRANSITION'][:50]}...")
    
    # Save results
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    freq_clean = freq_name.replace('MHz', '').replace('/', '_')
    
    # Save transition summary
    trans_file = os.path.join(output_dir, f"{freq_clean}_transitions.xlsx")
    transition_summary.to_excel(trans_file, index=False)
    print(f"\n💾 Saved transition analysis: {trans_file}")
    
    # Save summary stats
    summary_data = {
        'Frequency': freq_name,
        'Total_Rows': len(df),
        'GT_Rows': len(gt_df),
        'GT_Percentage': len(gt_df)/len(df)*100,
        **duration_stats,
        'Unique_Transitions': len(transition_summary)
    }
    
    return summary_data

def main():
    """Main function with menu."""
    frequencies = {
        '1': ('600MHz', r'\\samba.zsc3.intel.com\nfs\site\disks\fsintel\disk_001\apattnay\martini_wa\llama4-8tp-600Mhz'),
        '2': ('1000MHz', r'\\samba.zsc3.intel.com\nfs\site\disks\fsintel\disk_001\apattnay\martini_wa\llama4-8tp-1000Mhz'),
        '3': ('1600MHz', r'\\samba.zsc3.intel.com\nfs\site\disks\fsintel\disk_001\apattnay\martini_wa\llama4-8tp-1600Mhz'),
        '4': ('2000MHz', r'\\samba.zsc3.intel.com\nfs\site\disks\fsintel\disk_001\apattnay\martini_wa\llama4-8tp-2000Mhz'),
        'a': ('ALL', 'all')
    }
    
    print("🚀 SIMULATION RESULTS ANALYZER")
    print("=" * 50)
    print("Choose which frequency to analyze:")
    print("1. 600MHz")
    print("2. 1000MHz") 
    print("3. 1600MHz")
    print("4. 2000MHz")
    print("a. ALL frequencies (sequential)")
    print("-" * 50)
    
    choice = input("Enter your choice (1/2/3/4/a): ").strip().lower()
    
    if choice not in frequencies:
        print("❌ Invalid choice!")
        return
    
    all_summaries = []
    
    if choice == 'a':
        # Process all frequencies
        for key in ['1', '2', '3', '4']:
            freq_name, path = frequencies[key]
            summary = analyze_single_frequency(freq_name, path)
            if summary:
                all_summaries.append(summary)
            
            # Ask if user wants to continue
            if key != '4':
                cont = input(f"\n⏭️ Continue to next frequency? (y/n): ").strip().lower()
                if cont != 'y':
                    break
    else:
        # Process single frequency
        freq_name, path = frequencies[choice]
        summary = analyze_single_frequency(freq_name, path)
        if summary:
            all_summaries.append(summary)
    
    # Create final summary
    if all_summaries:
        print("\n" + "="*80)
        print("📋 FINAL SUMMARY")
        print("="*80)
        
        summary_df = pd.DataFrame(all_summaries)
        print(summary_df.to_string(index=False, float_format='%.6f'))
        
        # Save master summary
        os.makedirs("output", exist_ok=True)
        summary_df.to_excel("output/master_summary.xlsx", index=False)
        summary_df.to_csv("output/master_summary.csv", index=False)
        print("\n💾 Master summary saved to output/master_summary.xlsx")
        
        # Show total effort across all analyzed frequencies
        if len(all_summaries) > 1:
            total_effort = sum(s['total_duration'] for s in all_summaries)
            print(f"\n🎯 TOTAL EFFORT ACROSS ALL ANALYZED FREQUENCIES: {total_effort:,.6f}")

if __name__ == "__main__":
    main()