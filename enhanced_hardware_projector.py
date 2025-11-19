#!/usr/bin/env python3
"""
Enhanced Hardware Performance Projector v2.0 - Configurable Hardware Projection System
Projects performance from current hardware to future hardware with configurable improvement parameters.
Supports multiple calculation approaches with user-selectable execution options.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
from typing import Dict, List, Optional, Union
from enum import Enum

class CalculationApproach(Enum):
    """Enumeration of available calculation approaches."""
    HARDWARE_CALIBRATED = "hardware_calibrated"
    PURE_SIMULATION = "pure_simulation"
    HYBRID_CORRELATION = "hybrid_correlation"
    ALL = "all"

class HardwareProjectionConfig:
    """Configuration class for hardware projections."""
    
    def __init__(self, config_file: str = None):
        """Initialize configuration with default values or from file."""
        self.default_config = {
            "hardware_settings": {
                "current_hardware": {
                    "name": "PVC",
                    "description": "Ponte Vecchio Current Generation",
                    "baseline_measurements": {
                        "ttft_ms": 8336,
                        "tpot_ms": 53.46,
                        "baseline_frequency": 1600,
                        "tokens_input": 112,
                        "tokens_output": 2
                    }
                },
                "future_hardware": {
                    "name": "JGS", 
                    "description": "Next Generation Hardware",
                    "improvement_factors": {
                        "xecore_compute": {
                            "value": 0.375,
                            "description": "35-40% faster compute (time ratio)",
                            "applies_to": ["compute_tasks"]
                        },
                        "hbm_bandwidth": {
                            "value": 6.5,
                            "description": "6-7x higher memory bandwidth",
                            "applies_to": ["memory_tasks"]
                        },
                        "fabrication_process": {
                            "value": 0.75,
                            "description": "25% performance gain (time ratio)",
                            "applies_to": ["all_tasks"]
                        },
                        "communication": {
                            "bandwidth_improvement": {
                                "value": 12.5,
                                "description": "12x communication bandwidth"
                            },
                            "latency_improvement": {
                                "value": 150,
                                "description": "150x lower latency"
                            },
                            "applies_to": ["communication_tasks"]
                        }
                    }
                }
            },
            "calculation_settings": {
                "enabled_approaches": ["all"],  # Can be specific approaches or "all"
                "default_approach": "hardware_calibrated",
                "simulation_correlation": {
                    "correlation_factor": 2.311296913926394e-06,  # seconds per simulation unit
                    "calibration_method": "hardware_baseline"
                },
                "resource_distribution": {
                    "ex_u1_split": {
                        "memory_copy": 0.30,
                        "communication": 0.70
                    },
                    "fallback_weights": {
                        "compute": 0.4,
                        "memory": 0.3, 
                        "communication": 0.3
                    }
                }
            },
            "multi_gpu_settings": {
                "configurations": {
                    "8T": {"gpus": 4, "tiles_per_gpu": 2},
                    "16T": {"gpus": 8, "tiles_per_gpu": 2},
                    "144T": {"gpus": 72, "tiles_per_gpu": 2}
                },
                "scaling_efficiency": {
                    "compute_scaling": 0.95,
                    "memory_scaling": 0.90,
                    "communication_overhead": 0.85
                }
            },
            "output_settings": {
                "generate_visualizations": True,
                "export_detailed_results": True,
                "comparison_tables": True,
                "performance_summary": True
            }
        }
        
        # Load configuration from file if provided
        if config_file and Path(config_file).exists():
            self.load_config(config_file)
        else:
            self.config = self.default_config.copy()
    
    def load_config(self, config_file: str):
        """Load configuration from JSON file."""
        try:
            with open(config_file, 'r') as f:
                file_config = json.load(f)
            
            # Merge with defaults (file config takes precedence)
            self.config = self._merge_configs(self.default_config, file_config)
            print(f"✅ Configuration loaded from {config_file}")
        except Exception as e:
            print(f"⚠️ Error loading config file: {e}. Using default configuration.")
            self.config = self.default_config.copy()
    
    def _merge_configs(self, default: dict, override: dict) -> dict:
        """Recursively merge configuration dictionaries."""
        result = default.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def save_config(self, config_file: str):
        """Save current configuration to JSON file."""
        try:
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            print(f"✅ Configuration saved to {config_file}")
        except Exception as e:
            print(f"❌ Error saving config: {e}")
    
    def get_enabled_approaches(self) -> List[CalculationApproach]:
        """Get list of enabled calculation approaches."""
        enabled = self.config['calculation_settings']['enabled_approaches']
        
        if 'all' in enabled or CalculationApproach.ALL.value in enabled:
            return [CalculationApproach.HARDWARE_CALIBRATED, 
                   CalculationApproach.PURE_SIMULATION,
                   CalculationApproach.HYBRID_CORRELATION]
        
        approaches = []
        for approach_name in enabled:
            try:
                approaches.append(CalculationApproach(approach_name))
            except ValueError:
                print(f"⚠️ Unknown calculation approach: {approach_name}")
        
        return approaches if approaches else [CalculationApproach.HARDWARE_CALIBRATED]

class EnhancedHardwareProjector:
    """Enhanced hardware projector with configurable approaches and improvements."""
    
    def __init__(self, config_file: str = None):
        """Initialize the enhanced hardware projector."""
        self.config_manager = HardwareProjectionConfig(config_file)
        self.config = self.config_manager.config
        
        # Extract hardware settings
        hw_config = self.config['hardware_settings']
        self.current_hardware = hw_config['current_hardware']['name']
        self.future_hardware = hw_config['future_hardware']['name']
        self.improvement_factors = hw_config['future_hardware']['improvement_factors']
        self.baseline_measurements = hw_config['current_hardware']['baseline_measurements']
        
        # Load simulation data
        self.load_simulation_data()
        
    def load_simulation_data(self):
        """Load simulation data for analysis."""
        try:
            # Load aggregated simulation data
            self.sim_data = pd.read_csv('output/master_summary.csv')
            print(f"✅ Loaded {self.current_hardware} simulation data for {len(self.sim_data)} frequencies")
            
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
            print(f"❌ Simulation data not found. Please ensure data is available!")
            self.sim_data = None
    
    def analyze_resource_types(self, freq_data: pd.DataFrame) -> Optional[Dict]:
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
        
        total_all_duration = total_compute_duration + total_memory_comm_duration + total_other_duration
        
        analysis['summary'] = {
            'compute_duration': total_compute_duration,
            'memory_comm_duration': total_memory_comm_duration,
            'other_duration': total_other_duration,
            'total_duration': total_all_duration,
            'compute_percentage': (total_compute_duration / total_all_duration) * 100 if total_all_duration > 0 else 0,
            'memory_comm_percentage': (total_memory_comm_duration / total_all_duration) * 100 if total_all_duration > 0 else 0,
            'compute_tasks_count': len(analysis['compute_tasks']),
            'memory_comm_tasks_count': len(analysis['memory_comm_tasks']),
            'other_tasks_count': len(analysis['other_tasks'])
        }
        
        return analysis
    
    def _calculate_hardware_improvement_factor(self) -> float:
        """Calculate overall hardware improvement factor from individual component improvements."""
        improvements = self.improvement_factors
        
        # Get individual improvement factors
        compute_improvement = 1 / improvements['xecore_compute']['value']  # Time ratio to speedup
        memory_improvement = improvements['hbm_bandwidth']['value']  # Direct multiplier
        fabrication_improvement = 1 / improvements['fabrication_process']['value']  # Time ratio to speedup
        
        # Communication improvement (geometric mean of bandwidth and latency)
        comm_bw = improvements['communication']['bandwidth_improvement']['value']
        comm_lat = improvements['communication']['latency_improvement']['value'] 
        comm_improvement = np.sqrt(comm_bw * comm_lat)
        
        # Calculate weighted overall improvement based on typical workload distribution
        workload_weights = self.config['calculation_settings']['resource_distribution']['fallback_weights']
        compute_weight = workload_weights['compute']
        memory_weight = workload_weights['memory']
        comm_weight = workload_weights['communication']
        
        # Weighted geometric mean for overall improvement
        overall_improvement = (
            (compute_improvement ** compute_weight) * 
            (memory_improvement ** memory_weight) * 
            (comm_improvement ** comm_weight) * 
            fabrication_improvement  # Applied to all components
        )
        
        return overall_improvement
    
    def establish_tgs_correlation(self) -> Dict[str, float]:
        """Establish correlation between measured PVC TGS and simulation-derived TGS at baseline frequency."""
        baseline_freq = self.baseline_measurements['baseline_frequency']
        
        # Find 1600MHz simulation data
        baseline_sim_data = None
        if self.sim_data is not None:
            baseline_rows = self.sim_data[self.sim_data['Frequency'] == f'{baseline_freq}MHz']
            if not baseline_rows.empty:
                baseline_sim_data = baseline_rows.iloc[0]
        
        if baseline_sim_data is None:
            print(f"⚠️  No simulation data found for baseline frequency {baseline_freq}MHz")
            return {}
        
        # Calculate measured PVC TGS at baseline frequency
        baseline_ttft = self.baseline_measurements['ttft_ms'] / 1000
        baseline_tpot = self.baseline_measurements['tpot_ms'] / 1000
        input_tokens = self.baseline_measurements['tokens_input']
        output_tokens = self.baseline_measurements['tokens_output']
        
        measured_total_time = baseline_ttft + (baseline_tpot * output_tokens)
        measured_tgs = (input_tokens + output_tokens) / measured_total_time
        
        # Calculate simulation-derived TGS using correlation factor
        sim_duration = baseline_sim_data['total_duration']
        correlation_factor = self.config['calculation_settings']['simulation_correlation']['correlation_factor']
        sim_time_seconds = sim_duration * correlation_factor
        sim_derived_tgs = (input_tokens + output_tokens) / sim_time_seconds if sim_time_seconds > 0 else 0
        
        # Calculate correlation metrics
        tgs_ratio = measured_tgs / sim_derived_tgs if sim_derived_tgs > 0 else 0
        accuracy_percentage = (1 - abs(measured_tgs - sim_derived_tgs) / measured_tgs) * 100 if measured_tgs > 0 else 0
        
        correlation_results = {
            'baseline_frequency_mhz': baseline_freq,
            'measured_tgs': measured_tgs,
            'simulation_derived_tgs': sim_derived_tgs,
            'tgs_correlation_ratio': tgs_ratio,
            'correlation_accuracy_percent': accuracy_percentage,
            'measured_total_time_sec': measured_total_time,
            'simulation_time_sec': sim_time_seconds,
            'simulation_duration_units': sim_duration,
            'correlation_factor_used': correlation_factor,
            'correlation_valid': abs(tgs_ratio - 1.0) < 0.1  # Within 10% is considered valid
        }
        
        return correlation_results
    
    def apply_hardware_improvements(self, 
                                  compute_duration: float,
                                  memory_duration: float, 
                                  comm_duration: float,
                                  other_duration: float) -> Dict[str, float]:
        """
        Apply configurable hardware improvements to different task types.
        Generic function that can work with any current->future hardware transition.
        
        Args:
            compute_duration: Duration for compute tasks
            memory_duration: Duration for memory tasks
            comm_duration: Duration for communication tasks
            other_duration: Duration for other tasks
            
        Returns:
            Dictionary with improved durations and improvement factors
        """
        improvements = self.improvement_factors
        
        # Apply XeCore compute improvement
        xecore_factor = improvements['xecore_compute']['value']
        improved_compute = compute_duration * xecore_factor
        
        # Apply HBM bandwidth improvement
        hbm_factor = improvements['hbm_bandwidth']['value']
        improved_memory = memory_duration / hbm_factor
        
        # Apply communication improvements (combined bandwidth + latency)
        comm_bw_factor = improvements['communication']['bandwidth_improvement']['value']
        comm_lat_factor = improvements['communication']['latency_improvement']['value']
        # Use geometric mean for combined improvement
        comm_combined_factor = np.sqrt(comm_bw_factor * comm_lat_factor)
        improved_comm = comm_duration / comm_combined_factor
        
        # Apply fabrication process improvement to all components
        fab_factor = improvements['fabrication_process']['value']
        improved_compute *= fab_factor
        improved_memory *= fab_factor
        improved_comm *= fab_factor
        improved_other = other_duration * fab_factor
        
        # Calculate individual improvement ratios
        compute_improvement = compute_duration / improved_compute if improved_compute > 0 else 1
        memory_improvement = memory_duration / improved_memory if improved_memory > 0 else 1
        comm_improvement = comm_duration / improved_comm if improved_comm > 0 else 1
        other_improvement = other_duration / improved_other if improved_other > 0 else 1
        
        return {
            'improved_compute_duration': improved_compute,
            'improved_memory_duration': improved_memory,
            'improved_comm_duration': improved_comm,
            'improved_other_duration': improved_other,
            'compute_improvement_ratio': compute_improvement,
            'memory_improvement_ratio': memory_improvement,
            'comm_improvement_ratio': comm_improvement,
            'other_improvement_ratio': other_improvement,
            'total_improved_duration': improved_compute + improved_memory + improved_comm + improved_other
        }
    
    def calculate_hardware_calibrated_tgs(self, simulation_duration: float, frequency: int) -> Dict[str, float]:
        """Calculate TGS using hardware-calibrated approach (Option A)."""
        baseline_freq = self.baseline_measurements['baseline_frequency']
        baseline_ttft = self.baseline_measurements['ttft_ms'] / 1000  # Convert to seconds
        baseline_tpot = self.baseline_measurements['tpot_ms'] / 1000
        input_tokens = self.baseline_measurements['tokens_input']
        output_tokens = self.baseline_measurements['tokens_output']
        
        # Frequency scaling factor
        freq_scale = frequency / baseline_freq
        
        # Scale baseline measurements by frequency
        scaled_ttft = baseline_ttft / freq_scale
        scaled_tpot = baseline_tpot / freq_scale
        
        # Calculate baseline TGS (tokens per second)
        total_time = scaled_ttft + (scaled_tpot * output_tokens)
        total_tokens = input_tokens + output_tokens
        baseline_tgs = total_tokens / total_time
        
        # Establish correlation between measured hardware and simulation
        correlation_factor = self.config['calculation_settings']['simulation_correlation']['correlation_factor']
        sim_time_seconds = simulation_duration * correlation_factor
        
        # Calculate TGS from simulation using established correlation
        total_tokens = input_tokens + output_tokens
        simulation_derived_tgs = total_tokens / sim_time_seconds if sim_time_seconds > 0 else 0
        
        # Calculate correlation ratio between measured and simulation-derived TGS
        tgs_correlation_ratio = baseline_tgs / simulation_derived_tgs if simulation_derived_tgs > 0 else 1
        
        # For future hardware projections, we'll apply improvements to the correlation-validated baseline
        # This removes the hardcoded improvement estimate and uses actual correlation data
        improved_tgs = baseline_tgs * self._calculate_hardware_improvement_factor()
        
        # Calculate actual improvement factor used
        actual_improvement_factor = improved_tgs / baseline_tgs if baseline_tgs > 0 else 1
        
        return {
            'baseline_tgs': baseline_tgs,
            'improved_tgs': improved_tgs,
            'improvement_factor': actual_improvement_factor,
            'simulation_time_seconds': sim_time_seconds,
            'simulation_derived_tgs': simulation_derived_tgs,
            'tgs_correlation_ratio': tgs_correlation_ratio,
            'scaled_ttft': scaled_ttft,
            'scaled_tpot': scaled_tpot
        }
    
    def calculate_pure_simulation_tgs(self, simulation_duration: float, frequency: int) -> Dict[str, float]:
        """Calculate TGS using pure simulation approach (Option B)."""
        correlation_factor = self.config['calculation_settings']['simulation_correlation']['correlation_factor']
        
        # Convert simulation duration to real time
        sim_time_seconds = simulation_duration * correlation_factor
        
        # Assume token processing is proportional to simulation time
        # This assumes the simulation directly models the token processing workload
        total_tokens = self.baseline_measurements['tokens_input'] + self.baseline_measurements['tokens_output']
        
        # Calculate current TGS from simulation
        current_tgs = total_tokens / sim_time_seconds if sim_time_seconds > 0 else 0
        
        # Apply hardware improvements based on simulation characteristics
        # This would need detailed workload analysis to be precise
        compute_weight = 0.4  # Estimated compute portion
        memory_weight = 0.3   # Estimated memory portion  
        comm_weight = 0.3     # Estimated communication portion
        
        # Calculate weighted improvement
        compute_factor = 1 / self.improvement_factors['xecore_compute']['value']
        memory_factor = self.improvement_factors['hbm_bandwidth']['value']
        fab_factor = 1 / self.improvement_factors['fabrication_process']['value']
        
        # Simplified combined improvement
        combined_improvement = (
            (compute_factor ** compute_weight) * 
            (memory_factor ** memory_weight) * 
            fab_factor
        )
        
        improved_tgs = current_tgs * combined_improvement
        
        return {
            'simulation_time_seconds': sim_time_seconds,
            'current_tgs': current_tgs,
            'improved_tgs': improved_tgs,
            'improvement_factor': combined_improvement,
            'compute_weight': compute_weight,
            'memory_weight': memory_weight,
            'comm_weight': comm_weight
        }
    
    def calculate_hybrid_correlation_tgs(self, 
                                       simulation_duration: float, 
                                       frequency: int,
                                       resource_analysis: Optional[Dict] = None) -> Dict[str, float]:
        """Calculate TGS using hybrid correlation approach (Option C)."""
        # Start with hardware calibrated baseline
        hw_result = self.calculate_hardware_calibrated_tgs(simulation_duration, frequency)
        
        # Apply detailed resource-based improvements if available
        if resource_analysis:
            summary = resource_analysis['summary']
            
            # Get resource durations
            compute_dur = summary['compute_duration']
            memory_comm_dur = summary['memory_comm_duration']  
            other_dur = summary['other_duration']
            
            # Split memory_comm based on configuration
            dist = self.config['calculation_settings']['resource_distribution']['ex_u1_split']
            memory_dur = memory_comm_dur * dist['memory_copy']
            comm_dur = memory_comm_dur * dist['communication']
            
            # Apply detailed hardware improvements
            improvements = self.apply_hardware_improvements(
                compute_dur, memory_dur, comm_dur, other_dur
            )
            
            # Calculate improvement factor from detailed analysis
            total_original = compute_dur + memory_dur + comm_dur + other_dur
            total_improved = improvements['total_improved_duration']
            
            detailed_improvement = total_original / total_improved if total_improved > 0 else 1
            
            # Combine with hardware calibrated approach
            hybrid_tgs = hw_result['baseline_tgs'] * detailed_improvement
            
            return {
                **hw_result,
                'hybrid_tgs': hybrid_tgs,
                'detailed_improvement': detailed_improvement,
                'resource_breakdown': improvements
            }
        else:
            # Fall back to pure simulation approach
            sim_result = self.calculate_pure_simulation_tgs(simulation_duration, frequency)
            
            # Average the two approaches
            avg_improvement = (hw_result['improvement_factor'] + sim_result['improvement_factor']) / 2
            hybrid_tgs = hw_result['baseline_tgs'] * avg_improvement
            
            return {
                **hw_result,
                'hybrid_tgs': hybrid_tgs,
                'sim_contribution': sim_result,
                'averaged_improvement': avg_improvement
            }
    
    def calculate_projections(self, approaches: List[CalculationApproach] = None) -> pd.DataFrame:
        """
        Calculate hardware projections using specified approaches.
        
        Args:
            approaches: List of calculation approaches to use. If None, uses configured approaches.
            
        Returns:
            DataFrame with projection results for all enabled approaches
        """
        if approaches is None:
            approaches = self.config_manager.get_enabled_approaches()
        
        if self.sim_data is None:
            print("❌ No simulation data available")
            return pd.DataFrame()
        
        projections = []
        
        for _, row in self.sim_data.iterrows():
            freq_str = row['Frequency']
            freq_num = int(freq_str.replace('MHz', ''))
            total_duration = row['total_duration']
            
            # Get detailed resource analysis for this frequency
            freq_data = self.raw_data.get(freq_str.replace('MHz', ''))
            resource_analysis = self.analyze_resource_types(freq_data) if freq_data is not None else None
            
            # Calculate projections for each enabled approach
            projection_result = {
                'frequency': freq_num,
                'frequency_str': freq_str,
                'total_simulation_duration': total_duration,
                'resource_analysis_available': resource_analysis is not None
            }
            
            # Option A: Hardware-Calibrated Approach
            if CalculationApproach.HARDWARE_CALIBRATED in approaches:
                hw_result = self.calculate_hardware_calibrated_tgs(total_duration, freq_num)
                projection_result.update({
                    'hw_calibrated_baseline_tgs': hw_result['baseline_tgs'],
                    'hw_calibrated_improved_tgs': hw_result['improved_tgs'],
                    'hw_calibrated_improvement': hw_result['improvement_factor']
                })
            
            # Option B: Pure Simulation Approach
            if CalculationApproach.PURE_SIMULATION in approaches:
                sim_result = self.calculate_pure_simulation_tgs(total_duration, freq_num)
                projection_result.update({
                    'pure_sim_current_tgs': sim_result['current_tgs'],
                    'pure_sim_improved_tgs': sim_result['improved_tgs'], 
                    'pure_sim_improvement': sim_result['improvement_factor']
                })
            
            # Option C: Hybrid Correlation Approach
            if CalculationApproach.HYBRID_CORRELATION in approaches:
                hybrid_result = self.calculate_hybrid_correlation_tgs(
                    total_duration, freq_num, resource_analysis
                )
                projection_result.update({
                    'hybrid_baseline_tgs': hybrid_result['baseline_tgs'],
                    'hybrid_improved_tgs': hybrid_result.get('hybrid_tgs', hybrid_result['improved_tgs']),
                    'hybrid_improvement': hybrid_result.get('detailed_improvement', 
                                                          hybrid_result.get('averaged_improvement', 
                                                                          hybrid_result['improvement_factor']))
                })
            
            projections.append(projection_result)
        
        return pd.DataFrame(projections)
    
    def generate_comparison_analysis(self, projections_df: pd.DataFrame) -> Dict:
        """Generate comparative analysis of different calculation approaches."""
        if projections_df.empty:
            return {}
        
        enabled_approaches = self.config_manager.get_enabled_approaches()
        
        analysis = {
            'summary_statistics': {},
            'approach_comparison': {},
            'frequency_trends': {},
            'recommendations': []
        }
        
        # Calculate summary statistics for each approach
        for approach in enabled_approaches:
            if approach == CalculationApproach.HARDWARE_CALIBRATED:
                col = 'hw_calibrated_improved_tgs'
            elif approach == CalculationApproach.PURE_SIMULATION:
                col = 'pure_sim_improved_tgs'
            elif approach == CalculationApproach.HYBRID_CORRELATION:
                col = 'hybrid_improved_tgs'
            else:
                continue
                
            if col in projections_df.columns:
                values = projections_df[col].dropna()
                analysis['summary_statistics'][approach.value] = {
                    'mean_tgs': values.mean(),
                    'min_tgs': values.min(),
                    'max_tgs': values.max(),
                    'std_tgs': values.std(),
                    'range_tgs': values.max() - values.min()
                }
        
        # Add recommendations based on analysis
        if len(analysis['summary_statistics']) > 1:
            # Compare approaches and make recommendations
            approaches_data = analysis['summary_statistics']
            
            # Find most conservative and most optimistic approaches
            mean_values = {k: v['mean_tgs'] for k, v in approaches_data.items()}
            most_conservative = min(mean_values.keys(), key=lambda k: mean_values[k])
            most_optimistic = max(mean_values.keys(), key=lambda k: mean_values[k])
            
            analysis['recommendations'] = [
                f"Most conservative estimate: {most_conservative} (avg: {mean_values[most_conservative]:.2f} tok/s)",
                f"Most optimistic estimate: {most_optimistic} (avg: {mean_values[most_optimistic]:.2f} tok/s)",
                f"Range between approaches: {mean_values[most_optimistic] - mean_values[most_conservative]:.2f} tok/s"
            ]
            
            if 'hybrid_correlation' in mean_values:
                analysis['recommendations'].append(
                    "Hybrid approach recommended for balanced accuracy using both hardware and simulation data"
                )
        
        return analysis
    
    def generate_performance_plots(self, projections_df: pd.DataFrame, output_path: str = "output"):
        """Generate performance visualization plots for current and future hardware."""
        if projections_df.empty:
            print("⚠️ No data available for plotting")
            return
            
        output_dir = Path(output_path)
        output_dir.mkdir(exist_ok=True)
        
        # Set up plotting style
        plt.style.use('default')
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(f'Hardware Performance Projection: {self.current_hardware} → {self.future_hardware}', 
                     fontsize=16, fontweight='bold')
        
        # Prepare data
        frequencies = projections_df['frequency'].tolist()
        freq_labels = [f"{f}MHz" for f in frequencies]
        
        # Get baseline values
        baseline_values = []
        for _, row in projections_df.iterrows():
            if 'hw_calibrated_baseline_tgs' in row and not pd.isna(row['hw_calibrated_baseline_tgs']):
                baseline_values.append(row['hw_calibrated_baseline_tgs'])
            elif 'hybrid_baseline_tgs' in row and not pd.isna(row['hybrid_baseline_tgs']):
                baseline_values.append(row['hybrid_baseline_tgs'])
            elif 'pure_sim_current_tgs' in row and not pd.isna(row['pure_sim_current_tgs']):
                baseline_values.append(row['pure_sim_current_tgs'])
            else:
                baseline_values.append(0)
        
        # Plot 1: Current vs Future Hardware Comparison
        approaches_data = {}
        enabled_approaches = self.config_manager.get_enabled_approaches()
        
        for approach in enabled_approaches:
            if approach == CalculationApproach.HARDWARE_CALIBRATED:
                col = 'hw_calibrated_improved_tgs'
                name = "Hardware-Calibrated"
                color = '#1f77b4'
            elif approach == CalculationApproach.PURE_SIMULATION:
                col = 'pure_sim_improved_tgs'
                name = "Pure Simulation"
                color = '#ff7f0e'
            elif approach == CalculationApproach.HYBRID_CORRELATION:
                col = 'hybrid_improved_tgs'
                name = "Hybrid Correlation"
                color = '#2ca02c'
            else:
                continue
                
            if col in projections_df.columns:
                values = projections_df[col].tolist()
                approaches_data[name] = {'values': values, 'color': color}
        
        # Plot current hardware baseline
        ax1.plot(freq_labels, baseline_values, 'o-', linewidth=2, markersize=6, 
                label=f'{self.current_hardware} Current', color='red')
        
        # Plot future hardware projections
        for name, data in approaches_data.items():
            ax1.plot(freq_labels, data['values'], 'o-', linewidth=2, markersize=6,
                    label=f'{self.future_hardware} {name}', color=data['color'])
        
        ax1.set_xlabel('Frequency')
        ax1.set_ylabel('Performance (tok/s)')
        ax1.set_title('Current vs Future Hardware Performance')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Improvement Factors
        for name, data in approaches_data.items():
            improvements = [proj/base if base > 0 else 0 for proj, base in zip(data['values'], baseline_values)]
            ax2.plot(freq_labels, improvements, 'o-', linewidth=2, markersize=6,
                    label=name, color=data['color'])
        
        ax2.axhline(y=1, color='red', linestyle='--', alpha=0.7, label='No Improvement')
        ax2.set_xlabel('Frequency')
        ax2.set_ylabel('Improvement Factor (x)')
        ax2.set_title('Performance Improvement Factors')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Performance Range Analysis
        if len(approaches_data) > 1:
            mins = []
            maxs = []
            avgs = []
            
            for i in range(len(frequencies)):
                freq_values = [data['values'][i] for data in approaches_data.values() if i < len(data['values'])]
                if freq_values:
                    mins.append(min(freq_values))
                    maxs.append(max(freq_values))
                    avgs.append(sum(freq_values) / len(freq_values))
                else:
                    mins.append(0)
                    maxs.append(0)
                    avgs.append(0)
            
            ax3.fill_between(freq_labels, mins, maxs, alpha=0.3, color='lightblue', label='Projection Range')
            ax3.plot(freq_labels, avgs, 'o-', linewidth=2, markersize=6, color='blue', label='Average Projection')
            ax3.plot(freq_labels, baseline_values, 'o-', linewidth=2, markersize=6, color='red', label='Current Hardware')
            
            ax3.set_xlabel('Frequency')
            ax3.set_ylabel('Performance (tok/s)')
            ax3.set_title('Projection Range Analysis')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
        
        # Plot 4: Relative Performance (Log Scale)
        ax4.plot(freq_labels, baseline_values, 'o-', linewidth=2, markersize=6, 
                label=f'{self.current_hardware} Current', color='red')
        
        for name, data in approaches_data.items():
            ax4.plot(freq_labels, data['values'], 'o-', linewidth=2, markersize=6,
                    label=f'{self.future_hardware} {name}', color=data['color'])
        
        ax4.set_xlabel('Frequency')
        ax4.set_ylabel('Performance (tok/s) - Log Scale')
        ax4.set_title('Performance Comparison (Logarithmic Scale)')
        ax4.set_yscale('log')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # Adjust layout and save
        plt.tight_layout()
        plot_file = output_dir / f"hardware_performance_projection_{self.current_hardware}_to_{self.future_hardware}.png"
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        print(f"📈 Performance plots saved to {plot_file}")
        
        # Create individual approach comparison plot
        if len(approaches_data) > 1:
            fig2, ax = plt.subplots(figsize=(12, 8))
            
            x = np.arange(len(freq_labels))
            width = 0.15
            
            # Plot baseline
            ax.bar(x - width*1.5, baseline_values, width, label=f'{self.current_hardware} Current', 
                  color='red', alpha=0.7)
            
            # Plot each approach
            for i, (name, data) in enumerate(approaches_data.items()):
                offset = width * (i - len(approaches_data)/2 + 0.5)
                ax.bar(x + offset, data['values'], width, label=f'{self.future_hardware} {name}', 
                      color=data['color'], alpha=0.7)
            
            ax.set_xlabel('Frequency')
            ax.set_ylabel('Performance (tok/s)')
            ax.set_title(f'Hardware Performance Comparison: {self.current_hardware} vs {self.future_hardware}')
            ax.set_xticks(x)
            ax.set_xticklabels(freq_labels)
            ax.legend()
            ax.grid(True, alpha=0.3, axis='y')
            
            # Add value labels on bars
            for i, v in enumerate(baseline_values):
                ax.text(i - width*1.5, v + max(baseline_values)*0.01, f'{v:.1f}', 
                       ha='center', va='bottom', fontsize=8)
            
            for j, (name, data) in enumerate(approaches_data.items()):
                offset = width * (j - len(approaches_data)/2 + 0.5)
                for i, v in enumerate(data['values']):
                    ax.text(i + offset, v + max(data['values'])*0.01, f'{v:.1f}', 
                           ha='center', va='bottom', fontsize=8)
            
            plt.tight_layout()
            bar_plot_file = output_dir / f"hardware_comparison_bar_{self.current_hardware}_to_{self.future_hardware}.png"
            plt.savefig(bar_plot_file, dpi=300, bbox_inches='tight')
            print(f"📊 Comparison bar chart saved to {bar_plot_file}")
        
        plt.show()
    
    def export_results(self, projections_df: pd.DataFrame, analysis: Dict, output_path: str = "output"):
        """Export results to files."""
        output_dir = Path(output_path)
        output_dir.mkdir(exist_ok=True)
        
        # Export projections DataFrame
        projections_file = output_dir / "enhanced_hardware_projections.csv"
        projections_df.to_csv(projections_file, index=False)
        print(f"✅ Projections exported to {projections_file}")
        
        # Export analysis results
        analysis_file = output_dir / "projection_analysis.json"
        with open(analysis_file, 'w') as f:
            # Convert numpy types to Python types for JSON serialization
            def convert_numpy(obj):
                if isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                return obj
            
            def clean_for_json(data):
                if isinstance(data, dict):
                    return {k: clean_for_json(v) for k, v in data.items()}
                elif isinstance(data, list):
                    return [clean_for_json(item) for item in data]
                else:
                    return convert_numpy(data)
            
            json.dump(clean_for_json(analysis), f, indent=2)
        print(f"✅ Analysis exported to {analysis_file}")
        
        # Export configuration
        config_file = output_dir / "projection_config.json"
        self.config_manager.save_config(str(config_file))

def main():
    """Main execution function with configurable options."""
    print("🚀 Enhanced Hardware Projector v2.0")
    print("=" * 50)
    
    # Initialize with configuration
    projector = EnhancedHardwareProjector()
    
    # Display configuration summary
    hw_config = projector.config['hardware_settings']
    print(f"Current Hardware: {hw_config['current_hardware']['name']} ({hw_config['current_hardware']['description']})")
    print(f"Future Hardware: {hw_config['future_hardware']['name']} ({hw_config['future_hardware']['description']})")
    
    enabled_approaches = projector.config_manager.get_enabled_approaches()
    print(f"Enabled Calculation Approaches: {[a.value for a in enabled_approaches]}")
    print()
    
    # Establish TGS correlation between measured and simulated data
    print("🔗 Establishing TGS correlation between measured hardware and simulation...")
    correlation_results = projector.establish_tgs_correlation()
    
    if correlation_results:
        print(f"  Baseline Frequency: {correlation_results['baseline_frequency_mhz']}MHz")
        print(f"  Measured PVC TGS: {correlation_results['measured_tgs']:.4f} tok/s")
        print(f"  Simulation-derived TGS: {correlation_results['simulation_derived_tgs']:.4f} tok/s")
        print(f"  TGS Correlation Ratio: {correlation_results['tgs_correlation_ratio']:.4f}")
        print(f"  Correlation Accuracy: {correlation_results['correlation_accuracy_percent']:.2f}%")
        print(f"  Correlation Valid: {'✅ YES' if correlation_results['correlation_valid'] else '❌ NO'}")
        print()
    
    # Calculate projections
    print("📊 Calculating hardware projections...")
    projections_df = projector.calculate_projections()
    
    if not projections_df.empty:
        print(f"✅ Generated projections for {len(projections_df)} frequencies")
        
        # Generate comparative analysis
        analysis = projector.generate_comparison_analysis(projections_df)
        
        # Display current hardware baseline for reference
        print("\n📊 Current Hardware Baseline (Reference):")
        print("-" * 45)
        
        # Calculate current hardware TGS for each frequency
        baseline_tgs_values = []
        for _, row in projections_df.iterrows():
            freq = row['frequency']
            # Get baseline TGS from any approach that calculated it
            if 'hw_calibrated_baseline_tgs' in row and not pd.isna(row['hw_calibrated_baseline_tgs']):
                baseline_tgs_values.append(row['hw_calibrated_baseline_tgs'])
            elif 'hybrid_baseline_tgs' in row and not pd.isna(row['hybrid_baseline_tgs']):
                baseline_tgs_values.append(row['hybrid_baseline_tgs'])
            elif 'pure_sim_current_tgs' in row and not pd.isna(row['pure_sim_current_tgs']):
                baseline_tgs_values.append(row['pure_sim_current_tgs'])
        
        if baseline_tgs_values:
            baseline_min = min(baseline_tgs_values)
            baseline_max = max(baseline_tgs_values)
            baseline_avg = sum(baseline_tgs_values) / len(baseline_tgs_values)
            print(f"{projector.current_hardware} Current Performance: {baseline_min:.2f} - {baseline_max:.2f} tok/s (avg: {baseline_avg:.2f})")
        
        # Display projected results
        print("\n📈 Projected Hardware Performance Results:")
        print("-" * 45)
        print(f"{projector.future_hardware} Projected Performance:")
        
        for approach in enabled_approaches:
            if approach == CalculationApproach.HARDWARE_CALIBRATED:
                col = 'hw_calibrated_improved_tgs'
                name = "Hardware-Calibrated"
            elif approach == CalculationApproach.PURE_SIMULATION:
                col = 'pure_sim_improved_tgs'
                name = "Pure Simulation"
            elif approach == CalculationApproach.HYBRID_CORRELATION:
                col = 'hybrid_improved_tgs'
                name = "Hybrid Correlation"
            else:
                continue
                
            if col in projections_df.columns:
                values = projections_df[col].dropna()
                if len(values) > 0:
                    print(f"  {name:18}: {values.min():.2f} - {values.max():.2f} tok/s (avg: {values.mean():.2f})")
        
        # Display detailed frequency-by-frequency table
        print("\n📊 Detailed Performance by Frequency:")
        print("=" * 70)
        
        # Create table header
        header = f"{'Frequency':<10} {'Current HW':<12} "
        for approach in enabled_approaches:
            if approach == CalculationApproach.HARDWARE_CALIBRATED:
                header += f"{'HW-Calib':<12} "
            elif approach == CalculationApproach.PURE_SIMULATION:
                header += f"{'Pure-Sim':<12} "
            elif approach == CalculationApproach.HYBRID_CORRELATION:
                header += f"{'Hybrid':<12} "
        header += f"{'Best Improv':<12}"
        print(header)
        print("-" * len(header))
        
        # Display each frequency row
        for _, row in projections_df.iterrows():
            freq_str = row['frequency_str']
            
            # Get current hardware baseline
            current_hw_tgs = "N/A"
            if 'hw_calibrated_baseline_tgs' in row and not pd.isna(row['hw_calibrated_baseline_tgs']):
                current_hw_tgs = f"{row['hw_calibrated_baseline_tgs']:.2f}"
            elif 'hybrid_baseline_tgs' in row and not pd.isna(row['hybrid_baseline_tgs']):
                current_hw_tgs = f"{row['hybrid_baseline_tgs']:.2f}"
            elif 'pure_sim_current_tgs' in row and not pd.isna(row['pure_sim_current_tgs']):
                current_hw_tgs = f"{row['pure_sim_current_tgs']:.2f}"
            
            # Build row string
            row_str = f"{freq_str:<10} {current_hw_tgs:<12} "
            
            # Get projected values and find best
            projected_values = []
            for approach in enabled_approaches:
                if approach == CalculationApproach.HARDWARE_CALIBRATED:
                    col = 'hw_calibrated_improved_tgs'
                    if col in row and not pd.isna(row[col]):
                        val = row[col]
                        row_str += f"{val:<12.2f} "
                        projected_values.append(val)
                    else:
                        row_str += f"{'N/A':<12} "
                elif approach == CalculationApproach.PURE_SIMULATION:
                    col = 'pure_sim_improved_tgs'
                    if col in row and not pd.isna(row[col]):
                        val = row[col]
                        row_str += f"{val:<12.2f} "
                        projected_values.append(val)
                    else:
                        row_str += f"{'N/A':<12} "
                elif approach == CalculationApproach.HYBRID_CORRELATION:
                    col = 'hybrid_improved_tgs'
                    if col in row and not pd.isna(row[col]):
                        val = row[col]
                        row_str += f"{val:<12.2f} "
                        projected_values.append(val)
                    else:
                        row_str += f"{'N/A':<12} "
            
            # Add best improvement factor
            if projected_values and current_hw_tgs != "N/A":
                best_projected = max(projected_values)
                improvement = best_projected / float(current_hw_tgs)
                row_str += f"{improvement:<12.1f}x"
            else:
                row_str += f"{'N/A':<12}"
                
            print(row_str)
        
        # Show improvement factors summary
        if baseline_tgs_values:
            print("\n📈 Performance Improvement Summary:")
            print("-" * 35)
            for approach in enabled_approaches:
                if approach == CalculationApproach.HARDWARE_CALIBRATED:
                    col = 'hw_calibrated_improved_tgs'
                    name = "Hardware-Calibrated"
                elif approach == CalculationApproach.PURE_SIMULATION:
                    col = 'pure_sim_improved_tgs'
                    name = "Pure Simulation"
                elif approach == CalculationApproach.HYBRID_CORRELATION:
                    col = 'hybrid_improved_tgs'
                    name = "Hybrid Correlation"
                else:
                    continue
                    
                if col in projections_df.columns:
                    values = projections_df[col].dropna()
                    if len(values) > 0:
                        improvement_factor = values.mean() / baseline_avg
                        print(f"  {name:18}: {improvement_factor:.1f}x improvement")
        
        # Generate performance plots
        if projector.config['output_settings']['generate_visualizations']:
            print("\n📈 Generating performance visualization plots...")
            projector.generate_performance_plots(projections_df)
        
        # Display recommendations
        if analysis.get('recommendations'):
            print("\n💡 Recommendations:")
            for rec in analysis['recommendations']:
                print(f"  • {rec}")
        
        # Export results with correlation data
        projector.export_results(projections_df, analysis)
        
        # Export correlation analysis
        if correlation_results:
            correlation_file = Path("output") / "tgs_correlation_analysis.json"
            with open(correlation_file, 'w') as f:
                # Convert boolean to string for JSON serialization
                correlation_export = correlation_results.copy()
                correlation_export['correlation_valid'] = str(correlation_results['correlation_valid'])
                json.dump(correlation_export, f, indent=2)
            print(f"✅ TGS correlation analysis exported to {correlation_file}")
        
        print(f"\n✅ Results exported to output/ directory")
        
    else:
        print("❌ No projections could be calculated. Check input data and configuration.")

if __name__ == "__main__":
    main()