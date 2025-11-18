#!/usr/bin/env python3
"""
Hardware Performance Projector v1.0x - Advanced JGS Hardware Projection
Projects performance from PVC baseline to JGS hardware across multiple improvement parameters.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json

class HardwareProjector:
    def __init__(self):
        # Baseline Hardware: PVC (Ponte Vecchio)
        self.baseline_hardware = "PVC"
        self.target_hardware = "JGS"
        
        # Hardware improvement factors (JGS vs PVC)
        self.improvement_factors = {
            'xecore_compute': 0.375,      # 35-40% faster → 0.625-0.60 time ratio (using 37.5% improvement)
            'hbm_bandwidth': 6.5,         # 6-7x higher throughput
            'fabrication_process': 0.75,  # 25% perf gain → 0.75 time ratio  
            'communication': {
                'bandwidth_improvement': 12.5,  # ~12x bandwidth improvement
                'latency_improvement': 150      # ~150x lower latency
            }
        }
        
        # Task distribution for ex_u1 (Memory + Communication)
        self.ex_u1_distribution = {
            'memory_copy': 0.30,     # 30% MemoryCopy using HBMs
            'communication': 0.70    # 70% Communication
        }
        
        # Load baseline performance data
        self.load_baseline_data()
        
    def load_baseline_data(self):
        """Load PVC baseline performance data."""
        try:
            # Load simulation data for frequency analysis
            self.sim_data = pd.read_csv('output/master_summary.csv')
            print(f"✅ Loaded PVC baseline simulation data for {len(self.sim_data)} frequencies")
            
            # Load detailed raw CSV data for resource analysis
            self.raw_data = {}
            for freq in ['600', '1000', '1600', '2000']:
                try:
                    df = pd.read_csv(f'temp_data/{freq}mhz/simulation_results.csv')
                    # Filter for GT resources only
                    gt_df = df[df['RESOURCE'].str.contains('gt/', na=False)]
                    self.raw_data[freq] = gt_df
                    print(f"✅ Loaded {freq}MHz raw data: {len(gt_df)} GT resources")
                except FileNotFoundError:
                    print(f"⚠️ Raw data for {freq}MHz not found")
                    
        except FileNotFoundError:
            print("❌ Baseline data not found. Run universal_analyzer.py first!")
            self.sim_data = None
            
    def analyze_resource_types(self, freq_data):
        """Analyze and categorize resource types for hardware projection."""
        if freq_data is None or freq_data.empty:
            return None
            
        # Categorize resources based on RESOURCE column patterns
        analysis = {
            'compute_tasks': [],      # gt/GT_TILE_*/ex_u0 - XeCore compute tasks
            'memory_comm_tasks': [],  # gt/GT_TILE_*/ex_u1 - Memory + Communication tasks
            'other_tasks': []         # Other GT resources
        }
        
        total_compute_duration = 0
        total_memory_comm_duration = 0
        total_other_duration = 0
        
        try:
            # Ensure proper data types
            freq_data = freq_data.copy()
            freq_data['DURATION'] = pd.to_numeric(freq_data['DURATION'], errors='coerce')
            freq_data = freq_data.dropna(subset=['DURATION'])
            
            for idx, row in freq_data.iterrows():
                resource = str(row['RESOURCE'])
                duration = float(row['DURATION'])
                transition = str(row['TRANSITION'])
                
                if '/ex_u0' in resource and 'GT_TILE_' in resource:
                    # XeCore compute tasks
                    analysis['compute_tasks'].append({
                        'resource': resource,
                        'duration': duration,
                        'transition': transition
                    })
                    total_compute_duration += duration
                    
                elif '/ex_u1' in resource and 'GT_TILE_' in resource:
                    # Memory + Communication tasks
                    analysis['memory_comm_tasks'].append({
                        'resource': resource,
                        'duration': duration,
                        'transition': transition
                    })
                    total_memory_comm_duration += duration
                    
                elif resource.startswith('gt/'):
                    # Other GT resources
                    analysis['other_tasks'].append({
                        'resource': resource,
                        'duration': duration,
                        'transition': transition
                    })
                    total_other_duration += duration
        except Exception as e:
            print(f"⚠️ Error processing frequency data: {e}")
            return None
        
        analysis['summary'] = {
            'compute_duration': total_compute_duration,
            'memory_comm_duration': total_memory_comm_duration,
            'other_duration': total_other_duration,
            'total_duration': total_compute_duration + total_memory_comm_duration + total_other_duration,
            'compute_percentage': (total_compute_duration / (total_compute_duration + total_memory_comm_duration + total_other_duration)) * 100 if (total_compute_duration + total_memory_comm_duration + total_other_duration) > 0 else 0,
            'memory_comm_percentage': (total_memory_comm_duration / (total_compute_duration + total_memory_comm_duration + total_other_duration)) * 100 if (total_compute_duration + total_memory_comm_duration + total_other_duration) > 0 else 0,
            'compute_tasks_count': len(analysis['compute_tasks']),
            'memory_comm_tasks_count': len(analysis['memory_comm_tasks']),
            'other_tasks_count': len(analysis['other_tasks'])
        }
        
        return analysis
        
    def calculate_jgs_projections(self):
        """Calculate JGS hardware projections for all frequencies."""
        if self.sim_data is None:
            return None
            
        projections = []
        
        for _, row in self.sim_data.iterrows():
            freq_str = row['Frequency']
            freq_num = int(freq_str.replace('MHz', ''))
            pvc_duration = row['total_duration']
            
            # Get detailed resource analysis for this frequency
            freq_data = self.raw_data.get(freq_str.replace('MHz', ''))
            resource_analysis = self.analyze_resource_types(freq_data) if freq_data is not None else None
            
            if resource_analysis:
                # Detailed projection based on resource types
                compute_duration = resource_analysis['summary']['compute_duration']
                memory_comm_duration = resource_analysis['summary']['memory_comm_duration']
                other_duration = resource_analysis['summary']['other_duration']
                
                # Apply hardware improvements
                # 1. XeCore compute improvement (35-40% faster)
                jgs_compute_duration = compute_duration * self.improvement_factors['xecore_compute']
                
                # 2. Memory + Communication improvements (combined)
                memory_portion = memory_comm_duration * self.ex_u1_distribution['memory_copy']
                comm_portion = memory_comm_duration * self.ex_u1_distribution['communication']
                
                # Memory improvement: 6-7x HBM bandwidth
                jgs_memory_duration = memory_portion / self.improvement_factors['hbm_bandwidth']
                
                # Communication improvement: 12x bandwidth + 150x latency
                # Assume bandwidth improvement dominates for throughput, latency for responsiveness
                comm_bandwidth_factor = self.improvement_factors['communication']['bandwidth_improvement']
                comm_latency_factor = self.improvement_factors['communication']['latency_improvement']
                # Use geometric mean for combined improvement
                comm_combined_factor = np.sqrt(comm_bandwidth_factor * comm_latency_factor)
                jgs_comm_duration = comm_portion / comm_combined_factor
                
                # 3. Fabrication process improvement (25% gain)
                fabrication_factor = self.improvement_factors['fabrication_process']
                
                # Apply fabrication improvement to all components
                jgs_compute_duration *= fabrication_factor
                jgs_memory_duration *= fabrication_factor
                jgs_comm_duration *= fabrication_factor
                jgs_other_duration = other_duration * fabrication_factor  # Apply to other tasks too
                
                jgs_total_duration = jgs_compute_duration + jgs_memory_duration + jgs_comm_duration + jgs_other_duration
                
                # Calculate individual improvement factors
                compute_improvement = compute_duration / jgs_compute_duration if jgs_compute_duration > 0 else 1
                memory_improvement = memory_portion / jgs_memory_duration if jgs_memory_duration > 0 else 1
                comm_improvement = comm_portion / jgs_comm_duration if jgs_comm_duration > 0 else 1
                
            else:
                # Fallback: Apply combined improvement to total duration
                # Conservative estimate using geometric mean of all improvements
                xecore_factor = 1 / self.improvement_factors['xecore_compute']  # Convert to improvement ratio
                hbm_factor = self.improvement_factors['hbm_bandwidth']
                fab_factor = 1 / self.improvement_factors['fabrication_process']
                comm_factor = np.sqrt(self.improvement_factors['communication']['bandwidth_improvement'] * 
                                    self.improvement_factors['communication']['latency_improvement'])
                
                # Weighted combination (assuming 40% compute, 30% memory, 30% comm)
                combined_factor = (xecore_factor ** 0.4) * (hbm_factor ** 0.3) * (comm_factor ** 0.3) * fab_factor
                jgs_total_duration = pvc_duration / combined_factor
                
                # Individual components (estimated)
                compute_improvement = xecore_factor * fab_factor
                memory_improvement = hbm_factor * fab_factor
                comm_improvement = comm_factor * fab_factor
                
                jgs_compute_duration = pvc_duration * 0.4 / compute_improvement
                jgs_memory_duration = pvc_duration * 0.3 / memory_improvement
                jgs_comm_duration = pvc_duration * 0.3 / comm_improvement
                jgs_other_duration = 0
            
            # Calculate overall improvement
            overall_improvement = pvc_duration / jgs_total_duration if jgs_total_duration > 0 else 1
            
            projections.append({
                'frequency': freq_num,
                'frequency_str': freq_str,
                'pvc_duration': pvc_duration,
                'jgs_duration': jgs_total_duration,
                'overall_improvement': overall_improvement,
                'compute_improvement': compute_improvement,
                'memory_improvement': memory_improvement,
                'comm_improvement': comm_improvement,
                'jgs_compute_duration': jgs_compute_duration,
                'jgs_memory_duration': jgs_memory_duration,
                'jgs_comm_duration': jgs_comm_duration,
                'jgs_other_duration': jgs_other_duration,
                'performance_gain_percent': (overall_improvement - 1) * 100
            })
        
        return pd.DataFrame(projections)
        
    def project_llm_performance(self, hardware_df):
        """Project LLM performance (TTFT/TPOT/TGS) for JGS hardware."""
        # PVC baseline at 1600MHz
        baseline_ttft_ms = 8336  # 8.336 seconds
        baseline_tpot_ms = 53.46
        baseline_freq = 1600
        
        # Token configuration
        input_tokens = 112
        output_tokens = 2
        total_tokens = 114
        
        llm_projections = []
        
        for _, row in hardware_df.iterrows():
            freq = row['frequency']
            pvc_duration = row['pvc_duration']
            jgs_duration = row['jgs_duration']
            overall_improvement = row['overall_improvement']
            
            # Get PVC simulation duration ratio for frequency scaling
            if freq == baseline_freq:
                freq_scale_factor = 1.0
            else:
                baseline_sim_duration = hardware_df[hardware_df['frequency'] == baseline_freq]['pvc_duration'].iloc[0]
                freq_scale_factor = pvc_duration / baseline_sim_duration
            
            # Project PVC performance at this frequency
            pvc_ttft = baseline_ttft_ms * freq_scale_factor
            pvc_tpot = baseline_tpot_ms * freq_scale_factor
            pvc_total = pvc_ttft + pvc_tpot
            
            # Project JGS performance using hardware improvements
            jgs_ttft = pvc_ttft / overall_improvement
            jgs_tpot = pvc_tpot / overall_improvement
            jgs_total = jgs_ttft + jgs_tpot
            
            # Calculate Token Generation Speeds
            pvc_tgs = total_tokens / (pvc_total / 1000) if pvc_total > 0 else 0
            jgs_tgs = total_tokens / (jgs_total / 1000) if jgs_total > 0 else 0
            
            # Calculate output token rates
            pvc_output_rate = output_tokens / (pvc_tpot / 1000) if pvc_tpot > 0 else 0
            jgs_output_rate = output_tokens / (jgs_tpot / 1000) if jgs_tpot > 0 else 0
            
            llm_projections.append({
                'frequency': freq,
                'frequency_str': f"{freq}MHz",
                'pvc_ttft_ms': pvc_ttft,
                'pvc_tpot_ms': pvc_tpot,
                'pvc_total_ms': pvc_total,
                'pvc_tgs': pvc_tgs,
                'pvc_output_rate': pvc_output_rate,
                'jgs_ttft_ms': jgs_ttft,
                'jgs_tpot_ms': jgs_tpot,
                'jgs_total_ms': jgs_total,
                'jgs_tgs': jgs_tgs,
                'jgs_output_rate': jgs_output_rate,
                'llm_improvement': jgs_tgs / pvc_tgs if pvc_tgs > 0 else 1,
                'llm_improvement_percent': ((jgs_tgs / pvc_tgs) - 1) * 100 if pvc_tgs > 0 else 0
            })
        
        return pd.DataFrame(llm_projections)
        
    def create_hardware_comparison_visualizations(self, hardware_df, llm_df):
        """Create comprehensive hardware comparison visualizations."""
        plt.style.use('default')
        fig = plt.figure(figsize=(24, 18))
        
        # 1. Hardware Performance Comparison
        ax1 = plt.subplot(3, 4, 1)
        x_pos = range(len(hardware_df))
        width = 0.35
        
        plt.bar([x - width/2 for x in x_pos], hardware_df['pvc_duration'] / 1000000, 
                width, label='PVC (Baseline)', color='lightcoral', alpha=0.8)
        plt.bar([x + width/2 for x in x_pos], hardware_df['jgs_duration'] / 1000000, 
                width, label='JGS (Projected)', color='lightgreen', alpha=0.8)
        
        plt.title('Hardware Performance Comparison\n(Lower is Better)', fontweight='bold')
        plt.xlabel('Frequency')
        plt.ylabel('Duration (Million Units)')
        plt.xticks(x_pos, hardware_df['frequency_str'])
        plt.legend()
        plt.grid(axis='y', alpha=0.3)
        
        # 2. Improvement Factors Breakdown
        ax2 = plt.subplot(3, 4, 2)
        improvement_categories = ['XeCore\nCompute', 'HBM\nMemory', 'Communication', 'Overall']
        avg_improvements = [
            hardware_df['compute_improvement'].mean(),
            hardware_df['memory_improvement'].mean(), 
            hardware_df['comm_improvement'].mean(),
            hardware_df['overall_improvement'].mean()
        ]
        
        bars = plt.bar(improvement_categories, avg_improvements, 
                      color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'], alpha=0.8)
        
        # Add value labels
        for bar, val in zip(bars, avg_improvements):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                    f'{val:.1f}x', ha='center', va='bottom', fontweight='bold')
        
        plt.title('Hardware Improvement Factors\n(JGS vs PVC)', fontweight='bold')
        plt.ylabel('Improvement Factor (x)')
        plt.grid(axis='y', alpha=0.3)
        
        # 3. LLM Performance Comparison - TGS
        ax3 = plt.subplot(3, 4, 3)
        plt.bar([x - width/2 for x in x_pos], llm_df['pvc_tgs'], 
                width, label='PVC TGS', color='lightcoral', alpha=0.8)
        plt.bar([x + width/2 for x in x_pos], llm_df['jgs_tgs'], 
                width, label='JGS TGS', color='lightgreen', alpha=0.8)
        
        plt.title('Token Generation Speed\n(Higher is Better)', fontweight='bold')
        plt.xlabel('Frequency')
        plt.ylabel('Tokens per Second')
        plt.xticks(x_pos, llm_df['frequency_str'])
        plt.legend()
        plt.grid(axis='y', alpha=0.3)
        
        # 4. Enhanced LLM Performance Improvement
        ax4 = plt.subplot(3, 4, 4)
        
        # Create gradient colors based on improvement values
        improvement_values = llm_df['llm_improvement_percent']
        colors = ['#2E8B57' if x > 200 else '#32CD32' if x > 100 else '#90EE90' for x in improvement_values]
        
        bars = plt.bar(range(len(llm_df)), improvement_values, 
                      color=colors, alpha=0.8, edgecolor='black', linewidth=1)
        
        # Add enhanced value labels with improvement factor
        for i, (percent_val, factor_val) in enumerate(zip(improvement_values, llm_df['llm_improvement'])):
            # Main percentage label
            plt.text(i, percent_val + 10, f'{percent_val:+.0f}%', 
                    ha='center', va='bottom', fontweight='bold', fontsize=12)
            # Improvement factor label
            plt.text(i, percent_val/2, f'{factor_val:.1f}x', 
                    ha='center', va='center', fontweight='bold', fontsize=10, 
                    color='white', bbox=dict(boxstyle='round,pad=0.2', facecolor='black', alpha=0.7))
        
        plt.title('LLM Performance Improvement\n(JGS vs PVC Hardware)', fontweight='bold', fontsize=14)
        plt.xlabel('Frequency', fontweight='bold')
        plt.ylabel('Performance Improvement (%)', fontweight='bold')
        plt.xticks(range(len(llm_df)), llm_df['frequency_str'], fontweight='bold')
        
        # Enhanced baseline and grid
        plt.axhline(y=0, color='red', linestyle='--', alpha=0.8, linewidth=2, label='PVC Baseline')
        plt.grid(axis='y', alpha=0.4, linestyle=':', color='gray')
        
        # Add legend for baseline
        plt.legend(loc='upper left')
        
        # Set y-axis limits for better visualization
        plt.ylim(-50, max(improvement_values) + 50)
        
        # 5. TTFT Comparison
        ax5 = plt.subplot(3, 4, 5)
        plt.bar([x - width/2 for x in x_pos], llm_df['pvc_ttft_ms'] / 1000, 
                width, label='PVC TTFT', color='lightcoral', alpha=0.8)
        plt.bar([x + width/2 for x in x_pos], llm_df['jgs_ttft_ms'] / 1000, 
                width, label='JGS TTFT', color='lightgreen', alpha=0.8)
        
        plt.title('Time to First Token\n(Lower is Better)', fontweight='bold')
        plt.xlabel('Frequency')
        plt.ylabel('TTFT (seconds)')
        plt.xticks(x_pos, llm_df['frequency_str'])
        plt.legend()
        plt.grid(axis='y', alpha=0.3)
        
        # 6. TPOT Comparison
        ax6 = plt.subplot(3, 4, 6)
        plt.bar([x - width/2 for x in x_pos], llm_df['pvc_tpot_ms'], 
                width, label='PVC TPOT', color='lightcoral', alpha=0.8)
        plt.bar([x + width/2 for x in x_pos], llm_df['jgs_tpot_ms'], 
                width, label='JGS TPOT', color='lightgreen', alpha=0.8)
        
        plt.title('Time Per Output Token\n(Lower is Better)', fontweight='bold')
        plt.xlabel('Frequency')
        plt.ylabel('TPOT (ms)')
        plt.xticks(x_pos, llm_df['frequency_str'])
        plt.legend()
        plt.grid(axis='y', alpha=0.3)
        
        # 7. Hardware Component Duration Breakdown (JGS) - COMMENTED OUT
        # ax7 = plt.subplot(3, 4, 7)
        # bottom = np.zeros(len(hardware_df))
        # components = ['jgs_compute_duration', 'jgs_memory_duration', 'jgs_comm_duration', 'jgs_other_duration']
        # component_labels = ['Compute (XeCore)', 'Memory (HBM)', 'Communication', 'Other']
        # colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        # 
        # for i, (comp, label, color) in enumerate(zip(components, component_labels, colors)):
        #     values = hardware_df[comp] / 1000000  # Convert to millions
        #     plt.bar(x_pos, values, bottom=bottom, label=label, color=color, alpha=0.8)
        #     bottom += values
        # 
        # plt.title('JGS Duration Breakdown\n(Million Units)', fontweight='bold')
        # plt.xlabel('Frequency')
        # plt.ylabel('Duration (Million Units)')
        # plt.xticks(x_pos, hardware_df['frequency_str'])
        # plt.legend()
        
        # 8. Performance Scaling Trend - COMMENTED OUT
        # ax8 = plt.subplot(3, 4, 8)
        # plt.plot(hardware_df['frequency'], hardware_df['overall_improvement'], 
        #         'o-', linewidth=3, markersize=8, color='green', label='Hardware Improvement')
        # plt.plot(llm_df['frequency'], llm_df['llm_improvement'], 
        #         's--', linewidth=3, markersize=8, color='blue', label='LLM Performance')
        # 
        # plt.title('Improvement Scaling vs Frequency', fontweight='bold')
        # plt.xlabel('Frequency (MHz)')
        # plt.ylabel('Improvement Factor')
        # plt.legend()
        # plt.grid(alpha=0.3)
        
        # 7-8. Enhanced Summary Tables (using space from removed plots)
        ax9 = plt.subplot(3, 4, (7, 8))
        ax9.axis('tight')
        ax9.axis('off')
        
        # 9-12. Main Summary Tables
        ax10 = plt.subplot(3, 4, (9, 12))
        ax10.axis('tight')
        ax10.axis('off')
        
        # Create comprehensive summary table with GPU scaling
        # GPU configurations: 8 tiles (4 GPUs), 16 tiles (8 GPUs), 144 tiles (72 GPUs)
        gpu_configs = [
            {'tiles': 8, 'gpus': 4, 'label': '8T(4G)'},
            {'tiles': 16, 'gpus': 8, 'label': '16T(8G)'},
            {'tiles': 144, 'gpus': 72, 'label': '144T(72G)'}
        ]
        
        table_data = []
        for i, row in llm_df.iterrows():
            hardware_row = hardware_df.iloc[i]
            
            # Base performance (8 tiles baseline)
            base_pvc_tgs = row['pvc_tgs']
            base_jgs_tgs = row['jgs_tgs']
            base_pvc_ttft = row['pvc_ttft_ms']
            base_jgs_ttft = row['jgs_ttft_ms']
            
            for config in gpu_configs:
                scale_factor = config['tiles'] / 8  # Scale from 8-tile baseline
                
                # Scale TGS (higher parallelism = higher throughput)
                scaled_pvc_tgs = base_pvc_tgs * scale_factor
                scaled_jgs_tgs = base_jgs_tgs * scale_factor
                
                # TTFT scales with parallelism (more GPUs = faster first token)
                scaled_pvc_ttft = base_pvc_ttft / scale_factor
                scaled_jgs_ttft = base_jgs_ttft / scale_factor
                
                table_data.append([
                    f"{row['frequency_str']} {config['label']}",
                    f"{scaled_pvc_ttft/1000:.3f}s",
                    f"{row['pvc_tpot_ms']:.1f}ms",
                    f"{scaled_pvc_tgs:.1f}",
                    f"{scaled_jgs_ttft/1000:.3f}s",
                    f"{row['jgs_tpot_ms']:.1f}ms",
                    f"{scaled_jgs_tgs:.1f}", 
                    f"{row['llm_improvement']:.1f}x"
                ])
        
        table = ax10.table(cellText=table_data,
                          colLabels=['Config', 'PVC TTFT', 'PVC TPOT', 'PVC TGS\n(tok/s)', 
                                    'JGS TTFT', 'JGS TPOT', 'JGS TGS\n(tok/s)', 'HW Gain'],
                          cellLoc='center', loc='center')
        
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 1.8)
        
        # Style the table with GPU configuration highlighting
        total_rows = len(llm_df) * len(gpu_configs) + 1
        for i in range(total_rows):
            for j in range(8):  # Updated for 8 columns
                cell = table[(i, j)]
                if i == 0:  # Header
                    cell.set_facecolor('#2E8B57')
                    cell.set_text_props(weight='bold', color='white')
                else:
                    # Color code by GPU configuration
                    config_idx = (i - 1) % len(gpu_configs)
                    if config_idx == 0:  # 8 tiles
                        cell.set_facecolor('#e8f5e8')
                    elif config_idx == 1:  # 16 tiles  
                        cell.set_facecolor('#e8f0ff')
                    else:  # 144 tiles
                        cell.set_facecolor('#fff8e8')
        
        ax10.set_title('JGS Hardware Projection Summary\n(PVC to JGS Performance Gains)', 
                      fontsize=14, fontweight='bold', pad=15)
        
        plt.tight_layout()
        plt.savefig('output/jgs_hardware_projection.png', dpi=300, bbox_inches='tight')
        plt.savefig('jgs_hardware_projection.png', dpi=300, bbox_inches='tight')
        print("JGS hardware projection visualization saved")
        plt.close()
        
        return fig
        
    def generate_hardware_report(self, hardware_df, llm_df):
        """Generate detailed hardware projection report."""
        print("\n" + "="*100)
        print("JGS HARDWARE PROJECTION REPORT v1.0x - MULTI-GPU SCALING")
        print("="*100)
        print("📊 Hardware Transition: PVC (Ponte Vecchio) → JGS")
        print("🔧 GPU Architecture: 2 Tiles per GPU (both PVC and JGS)")
        print("📈 Scaling Configurations: 8T(4GPU), 16T(8GPU), 144T(72GPU)")
        print("\n🔧 IMPROVEMENT PARAMETERS:")
        print(f"   1. XeCore Compute (Xe4 vs Xe2): {1/self.improvement_factors['xecore_compute']:.1f}x faster")
        print(f"   2. HBM Bandwidth (HBM4e vs HBM2e): {self.improvement_factors['hbm_bandwidth']:.1f}x higher throughput")
        print(f"   3. Fabrication Process (18A vs 7nm): {1/self.improvement_factors['fabrication_process']:.1f}x performance gain")
        print(f"   4. Communication (UAL vs PCIe Gen5): {self.improvement_factors['communication']['bandwidth_improvement']:.1f}x bandwidth, {self.improvement_factors['communication']['latency_improvement']:.0f}x lower latency")
        
        print("\n📈 HARDWARE PERFORMANCE PROJECTIONS:")
        print("-" * 100)
        for _, row in hardware_df.iterrows():
            print(f"🎯 {row['frequency_str']:>8}: PVC={row['pvc_duration']/1000000:8.2f}M → JGS={row['jgs_duration']/1000000:6.2f}M | "
                  f"Gain={row['overall_improvement']:5.1f}x ({row['performance_gain_percent']:+5.1f}%)")
        
        print("\n🤖 LLM PERFORMANCE PROJECTIONS (Multi-GPU Scaling):")
        print("-" * 120)
        
        gpu_configs = [
            {'tiles': 8, 'gpus': 4, 'label': '8T(4GPU)'},
            {'tiles': 16, 'gpus': 8, 'label': '16T(8GPU)'},
            {'tiles': 144, 'gpus': 72, 'label': '144T(72GPU)'}
        ]
        
        for _, row in llm_df.iterrows():
            print(f"\n📊 {row['frequency_str']} Scaling:")
            for config in gpu_configs:
                scale_factor = config['tiles'] / 8
                scaled_pvc_tgs = row['pvc_tgs'] * scale_factor
                scaled_jgs_tgs = row['jgs_tgs'] * scale_factor
                scaled_jgs_ttft = row['jgs_ttft_ms'] / scale_factor / 1000
                
                print(f"   {config['label']:>12}: PVC={scaled_pvc_tgs:6.1f} -> JGS={scaled_jgs_tgs:6.1f} tok/s | "
                      f"TTFT={scaled_jgs_ttft:5.3f}s | Gain={row['llm_improvement']:4.1f}x")
        
        # Find best performance
        best_hw = hardware_df.loc[hardware_df['overall_improvement'].idxmax()]
        best_llm = llm_df.loc[llm_df['jgs_tgs'].idxmax()]
        
        print(f"\n🏆 BEST HARDWARE IMPROVEMENT: {best_hw['frequency_str']} → {best_hw['overall_improvement']:.1f}x gain")
        print(f"🏆 BEST LLM PERFORMANCE: {best_llm['frequency_str']} → {best_llm['jgs_tgs']:.2f} tokens/sec")
        
        avg_hw_improvement = hardware_df['overall_improvement'].mean()
        avg_llm_improvement = llm_df['llm_improvement'].mean()
        print(f"\n📊 AVERAGE IMPROVEMENTS: Hardware={avg_hw_improvement:.1f}x | LLM Performance={avg_llm_improvement:.1f}x")
        
        return hardware_df, llm_df

def main():
    """Run JGS hardware projection analysis."""
    print("🎯 Starting JGS Hardware Projection Analysis v1.0x...")
    
    projector = HardwareProjector()
    
    if projector.sim_data is None:
        print("❌ Cannot proceed without simulation data. Run universal_analyzer.py first!")
        return
    
    # Calculate hardware projections
    print("\n🔧 Calculating JGS hardware improvements...")
    hardware_df = projector.calculate_jgs_projections()
    
    if hardware_df is None:
        print("❌ Failed to calculate hardware projections!")
        return
    
    # Project LLM performance
    print("🤖 Projecting LLM performance for JGS hardware...")
    llm_df = projector.project_llm_performance(hardware_df)
    
    # Generate report
    projector.generate_hardware_report(hardware_df, llm_df)
    
    # Create visualizations  
    print("\n📊 Creating JGS hardware projection visualizations...")
    projector.create_hardware_comparison_visualizations(hardware_df, llm_df)
    
    # Save detailed results
    hardware_df.to_excel('output/jgs_hardware_projections.xlsx', index=False)
    llm_df.to_excel('output/jgs_llm_projections.xlsx', index=False)
    
    # Save combined results
    combined_df = pd.merge(hardware_df, llm_df, on=['frequency', 'frequency_str'])
    combined_df.to_csv('output/jgs_combined_projections.csv', index=False)
    
    print("\n✅ JGS Hardware Projection Analysis Complete!")
    print("📁 Files generated:")
    print("   - output/jgs_hardware_projection.png")
    print("   - output/jgs_hardware_projections.xlsx")
    print("   - output/jgs_llm_projections.xlsx") 
    print("   - output/jgs_combined_projections.csv")

if __name__ == "__main__":
    main()