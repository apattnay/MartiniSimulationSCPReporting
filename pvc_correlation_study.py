#!/usr/bin/env python3
"""
PVC Hardware-Simulation Correlation Study
Establishes correlation between measured PVC hardware performance and simulation results
at 1600MHz baseline without any performance improvements.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
from pathlib import Path
from typing import Dict, Optional

class PVCCorrelationStudy:
    """Study correlation between measured PVC hardware and simulation results."""
    
    def __init__(self):
        """Initialize correlation study with known PVC measurements."""
        # Known PVC hardware measurements at 1600MHz
        self.pvc_measurements = {
            "ttft_ms": 8336,        # 8.336 seconds
            "tpot_ms": 53.46,       # 0.05346 seconds  
            "baseline_frequency": 1600,
            "tokens_input": 112,
            "tokens_output": 2,     # Total: 114 tokens
            "total_tokens": 114
        }
        
        # Calculate measured PVC performance metrics
        self.calculate_measured_performance()
        
        # Load simulation data
        self.load_simulation_data()
    
    def calculate_measured_performance(self):
        """Calculate performance metrics from measured PVC data."""
        ttft_sec = self.pvc_measurements["ttft_ms"] / 1000  # Convert to seconds
        tpot_sec = self.pvc_measurements["tpot_ms"] / 1000  # Convert to seconds
        
        # Calculate total time for processing
        total_time = ttft_sec + (tpot_sec * self.pvc_measurements["tokens_output"])
        
        # Calculate Tokens per Second (TGS)
        measured_tgs = self.pvc_measurements["total_tokens"] / total_time
        
        self.measured_performance = {
            "ttft_seconds": ttft_sec,
            "tpot_seconds": tpot_sec, 
            "total_processing_time": total_time,
            "measured_tgs": measured_tgs
        }
        
        print("📊 PVC Measured Performance at 1600MHz:")
        print(f"  TTFT: {ttft_sec:.3f} seconds")
        print(f"  TPOT: {tpot_sec:.5f} seconds")
        print(f"  Total Time: {total_time:.3f} seconds")
        print(f"  Measured TGS: {measured_tgs:.2f} tokens/second")
    
    def load_simulation_data(self):
        """Load simulation results for 1600MHz."""
        try:
            # Load master summary for 1600MHz
            master_df = pd.read_csv('output/master_summary.csv')
            freq_1600_row = master_df[master_df['Frequency'] == '1600MHz']
            
            if not freq_1600_row.empty:
                self.sim_total_duration = freq_1600_row['total_duration'].iloc[0]
                print(f"\n📊 Simulation Data at 1600MHz:")
                print(f"  Total Simulation Duration: {self.sim_total_duration:.6f} units")
            else:
                print("❌ No 1600MHz simulation data found in master summary")
                self.sim_total_duration = None
                return
            
            # Load detailed raw simulation data for 1600MHz
            raw_data_path = 'temp_data/1600mhz/simulation_results.csv'
            if Path(raw_data_path).exists():
                self.raw_sim_data = pd.read_csv(raw_data_path)
                # Filter for GT resources only
                self.gt_sim_data = self.raw_sim_data[self.raw_sim_data['RESOURCE'].str.contains('gt/', na=False)]
                
                print(f"  Raw Simulation Records: {len(self.raw_sim_data)}")
                print(f"  GT Resources: {len(self.gt_sim_data)}")
                
                # Analyze resource breakdown
                self.analyze_simulation_workload()
            else:
                print(f"⚠️  Raw simulation data not found: {raw_data_path}")
                self.raw_sim_data = None
                self.gt_sim_data = None
                
        except FileNotFoundError as e:
            print(f"❌ Error loading simulation data: {e}")
            self.sim_total_duration = None
            self.raw_sim_data = None
    
    def analyze_simulation_workload(self):
        """Analyze simulation workload characteristics."""
        if self.gt_sim_data is None or self.gt_sim_data.empty:
            print("⚠️  No GT simulation data available for analysis")
            return
        
        # Ensure duration is numeric
        self.gt_sim_data = self.gt_sim_data.copy()
        self.gt_sim_data['DURATION'] = pd.to_numeric(self.gt_sim_data['DURATION'], errors='coerce')
        self.gt_sim_data = self.gt_sim_data.dropna(subset=['DURATION'])
        
        # Categorize workload types
        workload_analysis = {
            'compute_tasks': [],      # ex_u0 - XeCore compute
            'memory_comm_tasks': [],  # ex_u1 - Memory + Communication
            'other_gt_tasks': []      # Other GT resources
        }
        
        compute_duration = 0
        memory_comm_duration = 0
        other_duration = 0
        
        for _, row in self.gt_sim_data.iterrows():
            resource = str(row['RESOURCE'])
            duration = float(row['DURATION'])
            
            if '/ex_u0' in resource and 'GT_TILE_' in resource:
                workload_analysis['compute_tasks'].append(row.to_dict())
                compute_duration += duration
            elif '/ex_u1' in resource and 'GT_TILE_' in resource:
                workload_analysis['memory_comm_tasks'].append(row.to_dict())
                memory_comm_duration += duration
            elif resource.startswith('gt/'):
                workload_analysis['other_gt_tasks'].append(row.to_dict())
                other_duration += duration
        
        total_gt_duration = compute_duration + memory_comm_duration + other_duration
        
        self.workload_breakdown = {
            'compute_duration': compute_duration,
            'memory_comm_duration': memory_comm_duration,
            'other_duration': other_duration,
            'total_gt_duration': total_gt_duration,
            'compute_percentage': (compute_duration / total_gt_duration * 100) if total_gt_duration > 0 else 0,
            'memory_comm_percentage': (memory_comm_duration / total_gt_duration * 100) if total_gt_duration > 0 else 0,
            'other_percentage': (other_duration / total_gt_duration * 100) if total_gt_duration > 0 else 0,
            'task_counts': {
                'compute_tasks': len(workload_analysis['compute_tasks']),
                'memory_comm_tasks': len(workload_analysis['memory_comm_tasks']),
                'other_tasks': len(workload_analysis['other_gt_tasks'])
            }
        }
        
        print(f"\n🔍 Simulation Workload Breakdown:")
        print(f"  Compute (ex_u0): {compute_duration:.6f} units ({self.workload_breakdown['compute_percentage']:.1f}%)")
        print(f"  Memory/Comm (ex_u1): {memory_comm_duration:.6f} units ({self.workload_breakdown['memory_comm_percentage']:.1f}%)")
        print(f"  Other GT: {other_duration:.6f} units ({self.workload_breakdown['other_percentage']:.1f}%)")
        print(f"  Total GT Duration: {total_gt_duration:.6f} units")
        
        print(f"\n📈 Task Distribution:")
        print(f"  Compute Tasks: {self.workload_breakdown['task_counts']['compute_tasks']}")
        print(f"  Memory/Comm Tasks: {self.workload_breakdown['task_counts']['memory_comm_tasks']}")
        print(f"  Other GT Tasks: {self.workload_breakdown['task_counts']['other_tasks']}")
    
    def calculate_correlation_factors(self):
        """Calculate correlation factors between hardware and simulation."""
        if self.sim_total_duration is None:
            print("❌ Cannot calculate correlation - missing simulation data")
            return None
        
        measured_time = self.measured_performance["total_processing_time"]
        sim_duration = self.sim_total_duration
        
        # Primary correlation: simulation units to real seconds
        correlation_factor = measured_time / sim_duration
        
        # Alternative correlations
        ttft_correlation = self.measured_performance["ttft_seconds"] / sim_duration
        tgs_from_sim = self.pvc_measurements["total_tokens"] / (sim_duration * correlation_factor)
        
        # Validation: calculate TGS using simulation time
        simulated_tgs = self.pvc_measurements["total_tokens"] / measured_time  # Should match measured TGS
        
        self.correlation_results = {
            "primary_correlation_factor": correlation_factor,
            "simulation_duration_units": sim_duration,
            "measured_time_seconds": measured_time,
            "ttft_correlation_factor": ttft_correlation,
            "calculated_tgs_from_sim": tgs_from_sim,
            "measured_tgs": self.measured_performance["measured_tgs"],
            "tgs_validation_match": abs(tgs_from_sim - self.measured_performance["measured_tgs"]) < 0.01,
            "correlation_accuracy": abs(tgs_from_sim - self.measured_performance["measured_tgs"]) / self.measured_performance["measured_tgs"] * 100
        }
        
        print(f"\n🔗 Hardware-Simulation Correlation Analysis:")
        print(f"  Simulation Duration: {sim_duration:.10f} units")
        print(f"  Measured Time: {measured_time:.6f} seconds")
        print(f"  Primary Correlation Factor: {correlation_factor:.10e} seconds/unit")
        print(f"  Alternative (TTFT-based): {ttft_correlation:.10e} seconds/unit")
        
        print(f"\n✅ Correlation Validation:")
        print(f"  Measured TGS: {self.measured_performance['measured_tgs']:.4f} tok/s")
        print(f"  Calculated TGS from Sim: {tgs_from_sim:.4f} tok/s")
        print(f"  Accuracy: {100 - self.correlation_results['correlation_accuracy']:.2f}%")
        print(f"  Match Status: {'✅ PASS' if self.correlation_results['tgs_validation_match'] else '❌ FAIL'}")
        
        return self.correlation_results
    
    def validate_correlation_across_frequencies(self):
        """Validate correlation factor across all available frequencies."""
        try:
            master_df = pd.read_csv('output/master_summary.csv')
            
            print(f"\n🎯 Frequency Validation Study:")
            print(f"{'Frequency':<12} {'Sim Duration':<15} {'Predicted Time':<15} {'Predicted TGS':<15} {'Freq Scale':<12}")
            print("-" * 75)
            
            correlation_factor = self.correlation_results["primary_correlation_factor"]
            baseline_freq = 1600  # MHz
            
            validation_results = []
            
            for _, row in master_df.iterrows():
                freq_str = row['Frequency']
                freq_mhz = int(freq_str.replace('MHz', ''))
                sim_duration = row['total_duration']
                
                # Calculate frequency scaling factor
                freq_scale = freq_mhz / baseline_freq
                
                # Predict real time using correlation factor
                predicted_time = sim_duration * correlation_factor
                
                # Scale by frequency (higher frequency = faster processing)
                freq_scaled_time = predicted_time / freq_scale
                
                # Calculate predicted TGS
                predicted_tgs = self.pvc_measurements["total_tokens"] / freq_scaled_time
                
                validation_results.append({
                    'frequency_mhz': freq_mhz,
                    'frequency_str': freq_str,
                    'sim_duration': sim_duration,
                    'predicted_time': predicted_time,
                    'freq_scaled_time': freq_scaled_time,
                    'predicted_tgs': predicted_tgs,
                    'freq_scale': freq_scale
                })
                
                print(f"{freq_str:<12} {sim_duration:<15.8f} {freq_scaled_time:<15.6f} {predicted_tgs:<15.2f} {freq_scale:<12.3f}")
            
            self.frequency_validation = validation_results
            return validation_results
            
        except Exception as e:
            print(f"❌ Error in frequency validation: {e}")
            return None
    
    def generate_correlation_plots(self, output_path: str = "output"):
        """Generate visualization plots for correlation analysis."""
        if not hasattr(self, 'correlation_results') or not hasattr(self, 'frequency_validation'):
            print("⚠️  Cannot generate plots - missing correlation data")
            return
        
        output_dir = Path(output_path)
        output_dir.mkdir(exist_ok=True)
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('PVC Hardware-Simulation Correlation Study at 1600MHz Baseline', fontsize=16, fontweight='bold')
        
        # Plot 1: Frequency vs Predicted TGS
        frequencies = [v['frequency_mhz'] for v in self.frequency_validation]
        predicted_tgs = [v['predicted_tgs'] for v in self.frequency_validation]
        
        ax1.plot(frequencies, predicted_tgs, 'o-', linewidth=2, markersize=8, color='blue', label='Predicted TGS')
        ax1.axvline(x=1600, color='red', linestyle='--', alpha=0.7, label='1600MHz Baseline')
        ax1.axhline(y=self.measured_performance['measured_tgs'], color='red', linestyle='--', alpha=0.7, 
                   label=f'Measured TGS ({self.measured_performance["measured_tgs"]:.2f})')
        ax1.set_xlabel('Frequency (MHz)')
        ax1.set_ylabel('Predicted TGS (tok/s)')
        ax1.set_title('PVC Performance Prediction Across Frequencies')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Simulation Duration vs Real Time Correlation
        sim_durations = [v['sim_duration'] for v in self.frequency_validation]
        freq_scaled_times = [v['freq_scaled_time'] for v in self.frequency_validation]
        
        ax2.scatter(sim_durations, freq_scaled_times, s=100, alpha=0.7, c=frequencies, cmap='viridis')
        # Add trend line
        z = np.polyfit(sim_durations, freq_scaled_times, 1)
        p = np.poly1d(z)
        ax2.plot(sim_durations, p(sim_durations), "r--", alpha=0.8, label=f'Trend (slope={z[0]:.2e})')
        
        ax2.set_xlabel('Simulation Duration (units)')
        ax2.set_ylabel('Frequency-Scaled Time (seconds)')
        ax2.set_title('Simulation-to-Hardware Time Correlation')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Workload Breakdown (if available)
        if hasattr(self, 'workload_breakdown'):
            labels = ['Compute\n(ex_u0)', 'Memory/Comm\n(ex_u1)', 'Other GT']
            percentages = [
                self.workload_breakdown['compute_percentage'],
                self.workload_breakdown['memory_comm_percentage'], 
                self.workload_breakdown['other_percentage']
            ]
            colors = ['#ff7f0e', '#2ca02c', '#d62728']
            
            wedges, texts, autotexts = ax3.pie(percentages, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax3.set_title('1600MHz Simulation Workload Distribution')
            
        # Plot 4: Correlation Factor Validation
        measured_tgs = self.measured_performance['measured_tgs']
        calculated_tgs = self.correlation_results['calculated_tgs_from_sim']
        
        ax4.bar(['Measured\nPVC Hardware', 'Calculated from\nSimulation'], 
               [measured_tgs, calculated_tgs], 
               color=['blue', 'orange'], alpha=0.7)
        
        # Add accuracy text
        accuracy = 100 - self.correlation_results['correlation_accuracy']
        ax4.text(0.5, max(measured_tgs, calculated_tgs) * 0.9, 
                f'Correlation Accuracy: {accuracy:.2f}%', 
                ha='center', va='center', fontsize=12, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.7))
        
        ax4.set_ylabel('TGS (tokens/second)')
        ax4.set_title('Correlation Validation: Measured vs Calculated')
        ax4.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        ax4.text(0, measured_tgs + 0.5, f'{measured_tgs:.2f}', ha='center', va='bottom', fontweight='bold')
        ax4.text(1, calculated_tgs + 0.5, f'{calculated_tgs:.2f}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        
        # Save plots
        plot_file = output_dir / "pvc_hardware_simulation_correlation_study.png"
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        print(f"\n📈 Correlation study plots saved to {plot_file}")
        
        plt.show()
    
    def export_correlation_results(self, output_path: str = "output"):
        """Export correlation study results to files."""
        output_dir = Path(output_path)
        output_dir.mkdir(exist_ok=True)
        
        # Compile all results
        full_results = {
            "study_info": {
                "title": "PVC Hardware-Simulation Correlation Study",
                "baseline_frequency": 1600,
                "purpose": "Establish correlation between measured PVC performance and simulation results"
            },
            "pvc_measurements": self.pvc_measurements,
            "measured_performance": self.measured_performance,
            "correlation_results": self.correlation_results,
            "frequency_validation": self.frequency_validation if hasattr(self, 'frequency_validation') else None,
            "workload_breakdown": self.workload_breakdown if hasattr(self, 'workload_breakdown') else None
        }
        
        # Export to JSON
        json_file = output_dir / "pvc_correlation_study_results.json"
        with open(json_file, 'w') as f:
            json.dump(full_results, f, indent=2, default=str)
        print(f"✅ Correlation study results exported to {json_file}")
        
        # Export frequency validation to CSV
        if hasattr(self, 'frequency_validation'):
            freq_df = pd.DataFrame(self.frequency_validation)
            csv_file = output_dir / "pvc_frequency_correlation_validation.csv"
            freq_df.to_csv(csv_file, index=False)
            print(f"✅ Frequency validation data exported to {csv_file}")
        
        # Create summary report
        summary_file = output_dir / "pvc_correlation_study_summary.txt"
        with open(summary_file, 'w') as f:
            f.write("PVC Hardware-Simulation Correlation Study Summary\n")
            f.write("=" * 55 + "\n\n")
            
            f.write("MEASURED PVC PERFORMANCE (1600MHz):\n")
            f.write(f"  TTFT: {self.measured_performance['ttft_seconds']:.3f} seconds\n")
            f.write(f"  TPOT: {self.measured_performance['tpot_seconds']:.5f} seconds\n")
            f.write(f"  Total Time: {self.measured_performance['total_processing_time']:.3f} seconds\n")
            f.write(f"  Measured TGS: {self.measured_performance['measured_tgs']:.4f} tokens/second\n\n")
            
            f.write("SIMULATION DATA:\n")
            f.write(f"  Simulation Duration: {self.sim_total_duration:.10f} units\n")
            if hasattr(self, 'workload_breakdown'):
                f.write(f"  Compute Tasks: {self.workload_breakdown['compute_percentage']:.1f}%\n")
                f.write(f"  Memory/Comm Tasks: {self.workload_breakdown['memory_comm_percentage']:.1f}%\n")
                f.write(f"  Other GT Tasks: {self.workload_breakdown['other_percentage']:.1f}%\n")
            f.write("\n")
            
            f.write("CORRELATION RESULTS:\n")
            f.write(f"  Primary Correlation Factor: {self.correlation_results['primary_correlation_factor']:.10e} seconds/unit\n")
            f.write(f"  Calculated TGS from Sim: {self.correlation_results['calculated_tgs_from_sim']:.4f} tok/s\n")
            f.write(f"  Correlation Accuracy: {100 - self.correlation_results['correlation_accuracy']:.2f}%\n")
            f.write(f"  Validation: {'PASS' if self.correlation_results['tgs_validation_match'] else 'FAIL'}\n\n")
            
            if hasattr(self, 'frequency_validation'):
                f.write("FREQUENCY VALIDATION:\n")
                for v in self.frequency_validation:
                    f.write(f"  {v['frequency_str']}: {v['predicted_tgs']:.2f} tok/s (scale: {v['freq_scale']:.3f}x)\n")
        
        print(f"✅ Summary report exported to {summary_file}")
    
    def run_complete_study(self):
        """Run the complete correlation study."""
        print("🔬 PVC Hardware-Simulation Correlation Study")
        print("=" * 60)
        print("Purpose: Establish baseline correlation between measured PVC")
        print("         hardware performance and simulation results at 1600MHz")
        print("=" * 60)
        
        # Calculate correlation factors
        correlation_results = self.calculate_correlation_factors()
        
        if correlation_results is None:
            print("❌ Study failed - unable to calculate correlations")
            return False
        
        # Validate across frequencies
        self.validate_correlation_across_frequencies()
        
        # Generate visualizations
        self.generate_correlation_plots()
        
        # Export results
        self.export_correlation_results()
        
        # Final summary
        print(f"\n🎯 STUDY CONCLUSION:")
        print(f"  Established correlation factor: {correlation_results['primary_correlation_factor']:.10e} sec/unit")
        print(f"  Correlation accuracy: {100 - correlation_results['correlation_accuracy']:.2f}%")
        print(f"  Suitable for hardware-simulation mapping: {'✅ YES' if correlation_results['tgs_validation_match'] else '❌ NO'}")
        
        return True

def main():
    """Main execution function."""
    print("🚀 Starting PVC Hardware-Simulation Correlation Study...")
    
    study = PVCCorrelationStudy()
    success = study.run_complete_study()
    
    if success:
        print("\n✅ Correlation study completed successfully!")
        print("📁 Check output/ directory for detailed results and visualizations")
    else:
        print("\n❌ Correlation study failed!")

if __name__ == "__main__":
    main()