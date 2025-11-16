#!/usr/bin/env python3
"""
LLM Performance Projector - Projects TTFT and TPOT performance across frequencies
Based on simulation duration data and 1600MHz baseline performance.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

class LLMPerformanceProjector:
    def __init__(self):
        # Baseline performance at 1600MHz (Updated Nov 15, 2025)
        self.baseline_freq = 1600
        self.baseline_ttft = 8336  # ms (8.336 seconds)
        self.baseline_tpot = 53.46  # ms
        self.baseline_total = self.baseline_ttft + self.baseline_tpot  # 8389.46 ms
        
        # Token configuration for TGS calculation
        self.input_tokens = 112
        self.output_tokens = 2
        self.total_tokens = self.input_tokens + self.output_tokens  # 114 tokens
        
        # Load simulation results
        self.load_simulation_data()
    
    def load_simulation_data(self):
        """Load the master summary from previous analysis."""
        try:
            self.sim_data = pd.read_csv('output/master_summary.csv')
            print("✅ Loaded simulation data:")
            print(self.sim_data[['Frequency', 'total_duration', 'avg_duration']])
        except FileNotFoundError:
            print("❌ Master summary not found. Run auto_analyzer.py first!")
            self.sim_data = None
    
    def calculate_performance_projections(self):
        """Calculate projected TTFT and TPOT for all frequencies."""
        if self.sim_data is None:
            return None
        
        # Get baseline simulation duration for 1600MHz
        baseline_sim = self.sim_data[self.sim_data['Frequency'] == '1600MHz']
        if baseline_sim.empty:
            print("❌ 1600MHz baseline not found in simulation data!")
            return None
        
        baseline_sim_duration = baseline_sim['total_duration'].iloc[0]
        print(f"🎯 Baseline (1600MHz) simulation duration: {baseline_sim_duration:,.2f}")
        
        # Calculate performance scaling factors based on simulation durations
        results = []
        
        for _, row in self.sim_data.iterrows():
            freq_str = row['Frequency']
            freq_num = int(freq_str.replace('MHz', ''))
            sim_duration = row['total_duration']
            
            # Performance scaling: higher simulation duration = longer execution time
            # Assumption: Performance scales proportionally with simulation duration
            duration_ratio = sim_duration / baseline_sim_duration
            
            # Calculate projected performance metrics
            projected_ttft = self.baseline_ttft * duration_ratio
            projected_tpot = self.baseline_tpot * duration_ratio
            projected_total = projected_ttft + projected_tpot
            
            # Also calculate frequency-based theoretical scaling
            # Higher frequency should give better performance (inverse relationship)
            freq_ratio = self.baseline_freq / freq_num
            theoretical_ttft = self.baseline_ttft * freq_ratio
            theoretical_tpot = self.baseline_tpot * freq_ratio
            theoretical_total = theoretical_ttft + theoretical_tpot
            
            # Calculate Token Generation Speed (TGS) - tokens per second
            # For simulation-based projections
            projected_total_seconds = projected_total / 1000
            projected_tgs = self.total_tokens / projected_total_seconds if projected_total_seconds > 0 else 0
            
            # For theoretical projections  
            theoretical_total_seconds = theoretical_total / 1000
            theoretical_tgs = self.total_tokens / theoretical_total_seconds if theoretical_total_seconds > 0 else 0
            
            # Calculate output token rate (tokens per second for generation phase)
            projected_tpot_seconds = projected_tpot / 1000
            output_token_rate = self.output_tokens / projected_tpot_seconds if projected_tpot_seconds > 0 else 0
            
            results.append({
                'frequency': freq_num,
                'frequency_str': freq_str,
                'sim_duration': sim_duration,
                'duration_ratio': duration_ratio,
                'projected_ttft': projected_ttft,
                'projected_tpot': projected_tpot,
                'projected_total': projected_total,
                'theoretical_ttft': theoretical_ttft,
                'theoretical_tpot': theoretical_tpot,
                'theoretical_total': theoretical_total,
                'projected_tgs': projected_tgs,
                'theoretical_tgs': theoretical_tgs,
                'output_token_rate': output_token_rate,
                'performance_improvement': (self.baseline_total / projected_total - 1) * 100
            })
        
        return pd.DataFrame(results)
    
    def create_performance_visualizations(self, df):
        """Create comprehensive performance visualizations."""
        # Set up the plotting style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Create figure with subplots
        fig = plt.figure(figsize=(20, 15))
        
        # # 1. Total Performance Comparison
        # ax1 = plt.subplot(2, 3, 1)
        # x_pos = range(len(df))
        # bars = plt.bar(x_pos, df['projected_total'], alpha=0.7, color='skyblue', label='Simulation-based')
        # plt.bar(x_pos, df['theoretical_total'], alpha=0.7, color='orange', label='Frequency-based', width=0.6)
        
        # # Add value labels on bars
        # for i, (sim_val, theo_val) in enumerate(zip(df['projected_total'], df['theoretical_total'])):
        #     plt.text(i, sim_val + 10, f'{sim_val:.1f}ms', ha='center', va='bottom', fontweight='bold')
        #     plt.text(i, theo_val + 10, f'{theo_val:.1f}ms', ha='center', va='bottom', fontweight='bold', color='orange')
        
        # plt.title('Total LLM Performance (TTFT + TPOT)', fontsize=14, fontweight='bold')
        # plt.xlabel('Frequency')
        # plt.ylabel('Total Time (ms)')
        # plt.xticks(x_pos, df['frequency_str'])
        # plt.legend()
        # plt.grid(axis='y', alpha=0.3)
        
        # 2. TTFT vs TPOT Breakdown
        ax2 = plt.subplot(2, 3, 2)
        width = 0.35
        x_pos = np.arange(len(df))
        
        plt.bar(x_pos - width/2, df['projected_ttft'], width, label='TTFT', alpha=0.8, color='lightcoral')
        plt.bar(x_pos + width/2, df['projected_tpot'], width, label='TPOT', alpha=0.8, color='lightgreen')
        
        plt.title('TTFT vs TPOT Breakdown (Simulation-based)', fontsize=14, fontweight='bold')
        plt.xlabel('Frequency')
        plt.ylabel('Time (ms)')
        plt.xticks(x_pos, df['frequency_str'])
        plt.legend()
        plt.grid(axis='y', alpha=0.3)
        
        # # 3. Performance Improvement Chart
        # ax3 = plt.subplot(2, 3, 3)
        # colors = ['red' if x < 0 else 'green' for x in df['performance_improvement']]
        # bars = plt.bar(range(len(df)), df['performance_improvement'], color=colors, alpha=0.7)
        
        # # Add value labels
        # for i, val in enumerate(df['performance_improvement']):
        #     plt.text(i, val + (1 if val > 0 else -1), f'{val:+.1f}%', ha='center', 
        #             va='bottom' if val > 0 else 'top', fontweight='bold')
        
        # plt.title('Performance Change vs 1600MHz Baseline', fontsize=14, fontweight='bold')
        # plt.xlabel('Frequency')
        # plt.ylabel('Performance Change (%)')
        # plt.xticks(range(len(df)), df['frequency_str'])
        # plt.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        # plt.grid(axis='y', alpha=0.3)
        
        # # 4. Simulation Duration vs Performance
        # ax4 = plt.subplot(2, 3, 4)
        # scatter = plt.scatter(df['sim_duration'], df['projected_total'], 
        #                     c=df['frequency'], s=200, alpha=0.7, cmap='viridis')
        
        # # Add frequency labels
        # for i, row in df.iterrows():
        #     plt.annotate(row['frequency_str'], 
        #                 (row['sim_duration'], row['projected_total']),
        #                 xytext=(5, 5), textcoords='offset points', fontweight='bold')
        
        # plt.title('Simulation Duration vs Performance', fontsize=14, fontweight='bold')
        # plt.xlabel('Simulation Duration')
        # plt.ylabel('Total Performance (ms)')
        # plt.colorbar(scatter, label='Frequency (MHz)')
        # plt.grid(alpha=0.3)
        
        # 5. Frequency vs Performance Trend
        ax5 = plt.subplot(2, 3, 5)
        plt.plot(df['frequency'], df['projected_total'], 'o-', linewidth=3, markersize=10, 
                label='Simulation-based', color='blue')
        plt.plot(df['frequency'], df['theoretical_total'], 's--', linewidth=3, markersize=8, 
                label='Theoretical', color='red', alpha=0.7)
        
        # Highlight baseline
        baseline_row = df[df['frequency'] == 1600].iloc[0]
        plt.plot(1600, baseline_row['projected_total'], 'ro', markersize=15, 
                label=f'Baseline (1600MHz: {self.baseline_total}ms)', alpha=0.8)
        
        plt.title('Performance vs Frequency Trend', fontsize=14, fontweight='bold')
        plt.xlabel('Frequency (MHz)')
        plt.ylabel('Total Performance (ms)')
        plt.legend()
        plt.grid(alpha=0.3)
        
        # 6. Performance Summary Table
        ax6 = plt.subplot(2, 3, 6)
        ax6.axis('tight')
        ax6.axis('off')
        
        # Create table data
        table_data = []
        for _, row in df.iterrows():
            table_data.append([
                row['frequency_str'],
                f"{row['projected_ttft']:.0f}",
                f"{row['projected_tpot']:.1f}",
                f"{row['projected_total']:.0f}",
                f"{row['projected_tgs']:.2f}",
                f"{row['performance_improvement']:+.1f}%"
            ])
        
        table = ax6.table(cellText=table_data,
                         colLabels=['Frequency', 'TTFT (ms)', 'TPOT (ms)', 'Total (ms)', 'TGS (tok/s)', 'vs 1600MHz'],
                         cellLoc='center',
                         loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        
        # Style the table
        for i in range(len(df) + 1):
            for j in range(6):  # Updated for 6 columns
                cell = table[(i, j)]
                if i == 0:  # Header
                    cell.set_facecolor('#4CAF50')
                    cell.set_text_props(weight='bold', color='white')
                else:
                    cell.set_facecolor('#f0f0f0' if i % 2 == 0 else 'white')
        
        plt.title('Performance Summary Table', fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        plt.savefig('output/llm_performance_projection.png', dpi=300, bbox_inches='tight')
        plt.savefig('llm_performance_projection.png', dpi=300, bbox_inches='tight')  # Also save to root
        print("📊 Performance visualization saved to: output/llm_performance_projection.png")
        plt.close()  # Close instead of show to avoid GUI
        
        return fig
    
    def generate_report(self, df):
        """Generate a detailed performance report."""
        print("\n" + "="*80)
        print("🚀 LLM PERFORMANCE PROJECTION REPORT")
        print("="*80)
        print(f"📊 Baseline: 1600MHz → TTFT: {self.baseline_ttft:.1f}ms ({self.baseline_ttft/1000:.3f}s), TPOT: {self.baseline_tpot:.2f}ms")
        print(f"📊 Token Configuration: {self.input_tokens} input + {self.output_tokens} output = {self.total_tokens} total tokens")
        
        # Calculate baseline TGS
        baseline_tgs = self.total_tokens / (self.baseline_total / 1000)
        baseline_output_rate = self.output_tokens / (self.baseline_tpot / 1000)
        print(f"📊 Baseline TGS: {baseline_tgs:.2f} tokens/sec | Output Rate: {baseline_output_rate:.2f} tokens/sec")
        
        print("\n📈 PROJECTED PERFORMANCE ACROSS FREQUENCIES:")
        print("-"*120)
        
        for _, row in df.iterrows():
            improvement = "🚀" if row['performance_improvement'] > 0 else "⚠️" if row['performance_improvement'] < -10 else "📊"
            print(f"{improvement} {row['frequency_str']:>8}: TTFT={row['projected_ttft']:7.1f}ms | TPOT={row['projected_tpot']:6.2f}ms | "
                  f"Total={row['projected_total']:7.1f}ms | TGS={row['projected_tgs']:5.2f} tok/s | Change: {row['performance_improvement']:+5.1f}%")
        
        # Find best and worst performers
        best_freq = df.loc[df['projected_total'].idxmin()]
        worst_freq = df.loc[df['projected_total'].idxmax()]
        
        print(f"\n🏆 BEST PERFORMANCE: {best_freq['frequency_str']} → {best_freq['projected_total']:.1f}ms")
        print(f"⚠️ WORST PERFORMANCE: {worst_freq['frequency_str']} → {worst_freq['projected_total']:.1f}ms")
        
        performance_range = worst_freq['projected_total'] - best_freq['projected_total']
        print(f"📊 Performance Range: {performance_range:.1f}ms ({performance_range/best_freq['projected_total']*100:.1f}% variation)")
        
        return df

def main():
    """Run the LLM performance projection analysis."""
    print("🎯 Starting LLM Performance Projection Analysis...")
    
    projector = LLMPerformanceProjector()
    
    if projector.sim_data is None:
        print("❌ Cannot proceed without simulation data. Run auto_analyzer.py first!")
        return
    
    # Calculate projections
    performance_df = projector.calculate_performance_projections()
    
    if performance_df is None:
        print("❌ Failed to calculate performance projections!")
        return
    
    # Generate report
    projector.generate_report(performance_df)
    
    # Create visualizations
    print("\n📊 Creating performance visualizations...")
    fig = projector.create_performance_visualizations(performance_df)
    
    # Save detailed results
    performance_df.to_excel('output/llm_performance_projections.xlsx', index=False)
    performance_df.to_csv('output/llm_performance_projections.csv', index=False)
    
    print("\n✅ Analysis complete!")
    print("📁 Files generated:")
    print("   - output/llm_performance_projection.png")
    print("   - output/llm_performance_projections.xlsx")
    print("   - output/llm_performance_projections.csv")

if __name__ == "__main__":
    main()