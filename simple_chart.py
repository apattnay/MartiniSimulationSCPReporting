#!/usr/bin/env python3
"""
Simple LLM Performance Chart - Clean visualization for presentation
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def create_simple_performance_chart():
    """Create a clean, presentation-ready performance chart."""
    
    # Load the projection data
    try:
        df = pd.read_csv('output/llm_performance_projections.csv')
    except FileNotFoundError:
        print("❌ Run performance_projector.py first!")
        return
    
    # Set up the plot with a clean style
    plt.style.use('default')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Chart 1: Total Performance Comparison
    frequencies = df['frequency_str'].tolist()
    total_times = df['projected_total'].tolist()
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
    
    bars = ax1.bar(frequencies, total_times, color=colors, alpha=0.8, edgecolor='black', linewidth=1)
    
    # Add value labels on bars
    for bar, value in zip(bars, total_times):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 20,
                f'{value:.1f}ms', ha='center', va='bottom', fontweight='bold', fontsize=12)
    
    # Highlight the baseline
    baseline_idx = frequencies.index('1600MHz')
    bars[baseline_idx].set_color('#FFD93D')
    bars[baseline_idx].set_edgecolor('red')
    bars[baseline_idx].set_linewidth(3)
    
    ax1.set_title('LLM Token Generation Performance\n(TTFT + TPOT)', fontsize=16, fontweight='bold', pad=20)
    ax1.set_xlabel('Frequency', fontsize=14)
    ax1.set_ylabel('Total Time (ms)', fontsize=14)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    ax1.set_ylim(0, max(total_times) * 1.15)
    
    # Add baseline annotation
    ax1.annotate('Baseline\n(Real HW: 601.5ms)', 
                xy=(baseline_idx, total_times[baseline_idx]), 
                xytext=(baseline_idx, total_times[baseline_idx] + 200),
                ha='center', fontweight='bold', color='red',
                arrowprops=dict(arrowstyle='->', color='red', lw=2))
    
    # Chart 2: Performance Improvement vs Baseline
    improvements = df['performance_improvement'].tolist()
    colors_2 = ['red' if x < 0 else 'green' for x in improvements]
    
    bars2 = ax2.bar(frequencies, improvements, color=colors_2, alpha=0.7, edgecolor='black', linewidth=1)
    
    # Add value labels
    for bar, value in zip(bars2, improvements):
        height = bar.get_height()
        y_pos = height + (2 if height > 0 else -5)
        va = 'bottom' if height > 0 else 'top'
        ax2.text(bar.get_x() + bar.get_width()/2., y_pos,
                f'{value:+.1f}%', ha='center', va=va, fontweight='bold', fontsize=12)
    
    ax2.axhline(y=0, color='black', linestyle='-', alpha=0.8, linewidth=2)
    ax2.set_title('Performance Change vs 1600MHz\n(Positive = Better Performance)', fontsize=16, fontweight='bold', pad=20)
    ax2.set_xlabel('Frequency', fontsize=14)
    ax2.set_ylabel('Performance Change (%)', fontsize=14)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add performance indicators
    best_idx = np.argmax(improvements)
    worst_idx = np.argmin(improvements)
    
    ax2.annotate('🏆 Best', xy=(best_idx, improvements[best_idx]), 
                xytext=(best_idx, improvements[best_idx] + 10),
                ha='center', fontweight='bold', color='green', fontsize=12)
    
    ax2.annotate('⚠️ Worst', xy=(worst_idx, improvements[worst_idx]), 
                xytext=(worst_idx, improvements[worst_idx] - 15),
                ha='center', fontweight='bold', color='red', fontsize=12)
    
    plt.tight_layout()
    
    # Save the chart
    plt.savefig('output/llm_performance_simple.png', dpi=300, bbox_inches='tight')
    plt.savefig('output/llm_performance_simple.pdf', bbox_inches='tight')  # For presentations
    plt.show()
    
    # Print summary
    print("\n" + "="*70)
    print("📊 LLM PERFORMANCE PROJECTION SUMMARY")
    print("="*70)
    print("🎯 Baseline (1600MHz): TTFT=550ms, TPOT=51.5ms → Total=601.5ms")
    print("\n📈 Projected Performance:")
    for i, row in df.iterrows():
        status = "🚀" if row['performance_improvement'] > 0 else "⚠️"
        print(f"   {status} {row['frequency_str']:>8}: {row['projected_total']:6.1f}ms ({row['performance_improvement']:+5.1f}%)")
    
    print(f"\n🏆 Best: 2000MHz → {df.loc[df['projected_total'].idxmin(), 'projected_total']:.1f}ms")
    print(f"⚠️ Worst: 600MHz → {df.loc[df['projected_total'].idxmax(), 'projected_total']:.1f}ms")
    print(f"\n💡 Key Insight: Higher frequencies deliver better LLM performance!")

if __name__ == "__main__":
    create_simple_performance_chart()