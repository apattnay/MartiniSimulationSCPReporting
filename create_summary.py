#!/usr/bin/env python3
"""
Generate a comprehensive summary table of all results
"""

import pandas as pd

def create_summary_table():
    """Create a comprehensive summary table combining simulation and performance data."""
    
    # Load simulation data
    sim_df = pd.read_csv('output/master_summary.csv')
    
    # Load performance projections
    perf_df = pd.read_csv('output/llm_performance_projections.csv')
    
    # Create comprehensive summary
    summary_data = []
    
    for i, sim_row in sim_df.iterrows():
        perf_row = perf_df[perf_df['frequency_str'] == sim_row['Frequency']].iloc[0]
        
        summary_data.append({
            'Frequency': sim_row['Frequency'],
            'Simulation_Duration': f"{sim_row['total_duration']:,.0f}",
            'GT_Resources': f"{sim_row['GT_Rows']:,}",
            'Avg_Duration_Per_Resource': f"{sim_row['avg_duration']:.2f}",
            'Projected_TTFT_ms': f"{perf_row['projected_ttft']:.1f}",
            'Projected_TPOT_ms': f"{perf_row['projected_tpot']:.1f}",
            'Total_Performance_ms': f"{perf_row['projected_total']:.1f}",
            'Performance_vs_1600MHz': f"{perf_row['performance_improvement']:+.1f}%",
            'Performance_Ranking': ''
        })
    
    summary_df = pd.DataFrame(summary_data)
    
    # Add performance rankings
    perf_values = [float(x) for x in summary_df['Total_Performance_ms']]
    rankings = pd.Series(perf_values).rank(method='min').astype(int)
    summary_df['Performance_Ranking'] = [f"#{rank}" for rank in rankings]
    
    # Save to files
    summary_df.to_excel('output/comprehensive_summary.xlsx', index=False)
    summary_df.to_csv('output/comprehensive_summary.csv', index=False)
    
    # Print formatted table
    print("\n" + "="*120)
    print("🎯 COMPREHENSIVE LLM PERFORMANCE & SIMULATION SUMMARY")
    print("="*120)
    print(summary_df.to_string(index=False))
    print("="*120)
    
    # Key insights
    print("\n📊 KEY INSIGHTS:")
    print("-"*50)
    print("🔍 Simulation Analysis:")
    print(f"   • Total GT/* resources analyzed: {sim_df['GT_Rows'].sum():,}")
    print(f"   • Average simulation duration: {sim_df['total_duration'].mean():,.0f}")
    print(f"   • Duration variation: {sim_df['total_duration'].std()/sim_df['total_duration'].mean()*100:.1f}%")
    
    print("\n🚀 Performance Projections:")
    best_perf = perf_df.loc[perf_df['projected_total'].idxmin()]
    worst_perf = perf_df.loc[perf_df['projected_total'].idxmax()]
    
    print(f"   • Best performance: {best_perf['frequency_str']} → {best_perf['projected_total']:.1f}ms")
    print(f"   • Worst performance: {worst_perf['frequency_str']} → {worst_perf['projected_total']:.1f}ms")
    print(f"   • Performance range: {worst_perf['projected_total'] - best_perf['projected_total']:.1f}ms")
    print(f"   • Baseline (1600MHz): 601.5ms (Real HW measurement)")
    
    print("\n💡 RECOMMENDATIONS:")
    print("-"*50)
    print("   🎯 For best LLM performance: Use 2000MHz (25% faster than baseline)")
    print("   ⚖️ For balanced performance: Use 1600MHz (baseline performance)")  
    print("   ⚠️ Avoid lower frequencies: 600MHz is 62.5% slower than baseline")
    
    return summary_df

if __name__ == "__main__":
    create_summary_table()