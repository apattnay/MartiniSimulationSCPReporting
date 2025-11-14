import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os
from typing import Dict, List, Tuple

class SimulationAnalyzer:
    """
    Analyzes simulation_results.csv files from multiple frequency sweep directories.
    Filters for gt/* resource types, sums durations, and creates effort estimations.
    """
    
    def __init__(self):
        self.frequency_paths = {
            '600MHz': r'\\samba.zsc3.intel.com\nfs\site\disks\fsintel\disk_001\apattnay\martini_wa\llama4-8tp-600Mhz',
            '1000MHz': r'\\samba.zsc3.intel.com\nfs\site\disks\fsintel\disk_001\apattnay\martini_wa\llama4-8tp-1000Mhz',
            '1600MHz': r'\\samba.zsc3.intel.com\nfs\site\disks\fsintel\disk_001\apattnay\martini_wa\llama4-8tp-1600Mhz',
            '2000MHz': r'\\samba.zsc3.intel.com\nfs\site\disks\fsintel\disk_001\apattnay\martini_wa\llama4-8tp-2000Mhz'
        }
        self.results = {}
        
    def load_csv_file(self, file_path: str) -> pd.DataFrame:
        """Load and return CSV file as DataFrame with progress indication."""
        try:
            print(f"Loading {file_path}...")
            print("  This may take a moment for large files...")
            
            # Load in chunks for better memory management
            chunk_size = 50000
            chunks = []
            total_rows = 0
            
            for chunk in pd.read_csv(file_path, chunksize=chunk_size):
                chunks.append(chunk)
                total_rows += len(chunk)
                print(f"  Loaded {total_rows:,} rows...", end='\r')
            
            df = pd.concat(chunks, ignore_index=True)
            print(f"\n✓ Successfully loaded {file_path}")
            print(f"  Shape: {df.shape}")
            print(f"  Columns: {df.columns.tolist()}")
            return df
        except KeyboardInterrupt:
            print(f"\n⚠ Loading interrupted for {file_path}")
            return pd.DataFrame()
        except Exception as e:
            print(f"\n✗ Error loading {file_path}: {e}")
            return pd.DataFrame()
    
    def filter_gt_resources(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter DataFrame for RESOURCE column containing 'gt/' patterns."""
        if 'RESOURCE' not in df.columns:
            print("Warning: RESOURCE column not found in DataFrame")
            return pd.DataFrame()
        
        # Filter for resources that start with 'gt/'
        gt_mask = df['RESOURCE'].str.startswith('gt/', na=False)
        filtered_df = df[gt_mask].copy()
        
        print(f"Filtered {len(filtered_df)} rows with gt/* resources from {len(df)} total rows")
        return filtered_df
    
    def calculate_duration_summary(self, df: pd.DataFrame) -> Dict:
        """Calculate duration summaries for the filtered data."""
        if df.empty or 'DURATION' not in df.columns:
            return {'total_duration': 0, 'avg_duration': 0, 'count': 0}
        
        # Convert DURATION to numeric, handling any non-numeric values
        df['DURATION'] = pd.to_numeric(df['DURATION'], errors='coerce')
        
        summary = {
            'total_duration': df['DURATION'].sum(),
            'avg_duration': df['DURATION'].mean(),
            'median_duration': df['DURATION'].median(),
            'max_duration': df['DURATION'].max(),
            'min_duration': df['DURATION'].min(),
            'count': len(df),
            'std_duration': df['DURATION'].std()
        }
        
        return summary
    
    def analyze_transitions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Analyze transitions and create effort estimation summary."""
        if df.empty or 'TRANSITION' not in df.columns:
            return pd.DataFrame()
        
        # Group by transition and calculate statistics
        transition_summary = df.groupby('TRANSITION').agg({
            'DURATION': ['count', 'sum', 'mean', 'median', 'std', 'min', 'max']
        }).round(4)
        
        # Flatten column names
        transition_summary.columns = ['_'.join(col).strip() for col in transition_summary.columns]
        transition_summary = transition_summary.reset_index()
        
        return transition_summary
    
    def process_frequency_sweep(self, frequency: str, path: str) -> Dict:
        """Process a single frequency sweep directory."""
        print(f"\n{'='*50}")
        print(f"Processing {frequency} at path: {path}")
        print(f"{'='*50}")
        
        csv_file = os.path.join(path, 'simulation_results.csv')
        
        # Check if file exists
        if not os.path.exists(csv_file):
            print(f"Warning: simulation_results.csv not found at {csv_file}")
            return {'error': f'File not found: {csv_file}'}
        
        # Load CSV
        df = self.load_csv_file(csv_file)
        if df.empty:
            return {'error': f'Failed to load or empty file: {csv_file}'}
        
        # Filter for gt/* resources
        gt_filtered = self.filter_gt_resources(df)
        if gt_filtered.empty:
            print("No gt/* resources found in the data")
            return {'error': 'No gt/* resources found'}
        
        # Calculate duration summary
        duration_summary = self.calculate_duration_summary(gt_filtered)
        
        # Analyze transitions
        transition_analysis = self.analyze_transitions(gt_filtered)
        
        # Store unique resources and transitions for reference
        unique_resources = gt_filtered['RESOURCE'].unique().tolist() if 'RESOURCE' in gt_filtered.columns else []
        unique_transitions = gt_filtered['TRANSITION'].unique().tolist() if 'TRANSITION' in gt_filtered.columns else []
        
        result = {
            'frequency': frequency,
            'path': path,
            'total_rows': len(df),
            'gt_filtered_rows': len(gt_filtered),
            'duration_summary': duration_summary,
            'transition_analysis': transition_analysis,
            'unique_resources': unique_resources,
            'unique_transitions': unique_transitions,
            'raw_data': gt_filtered
        }
        
        return result
    
    def run_analysis(self) -> Dict:
        """Run analysis for all frequency sweeps."""
        print("Starting Simulation Results Analysis")
        print("="*60)
        
        all_results = {}
        
        for i, (freq, path) in enumerate(self.frequency_paths.items(), 1):
            print(f"\nProcessing {i}/4: {freq}")
            try:
                result = self.process_frequency_sweep(freq, path)
                all_results[freq] = result
                self.results[freq] = result
                print(f"✓ Completed {freq}")
            except KeyboardInterrupt:
                print(f"\n⚠ Analysis interrupted at {freq}")
                break
            except Exception as e:
                print(f"✗ Error processing {freq}: {e}")
                all_results[freq] = {'error': str(e)}
                self.results[freq] = {'error': str(e)}
        
        return all_results
    
    def create_summary_report(self) -> pd.DataFrame:
        """Create a comprehensive summary report across all frequencies."""
        summary_data = []
        
        for freq, result in self.results.items():
            if 'error' in result:
                summary_data.append({
                    'Frequency': freq,
                    'Status': 'Error',
                    'Error': result['error'],
                    'Total_Duration': 0,
                    'Avg_Duration': 0,
                    'Transition_Count': 0,
                    'Resource_Count': 0
                })
            else:
                duration_sum = result['duration_summary']
                summary_data.append({
                    'Frequency': freq,
                    'Status': 'Success',
                    'Total_Rows': result['total_rows'],
                    'GT_Filtered_Rows': result['gt_filtered_rows'],
                    'Total_Duration': duration_sum['total_duration'],
                    'Avg_Duration': duration_sum['avg_duration'],
                    'Median_Duration': duration_sum['median_duration'],
                    'Max_Duration': duration_sum['max_duration'],
                    'Min_Duration': duration_sum['min_duration'],
                    'Std_Duration': duration_sum['std_duration'],
                    'Transition_Count': len(result['unique_transitions']),
                    'Resource_Count': len(result['unique_resources'])
                })
        
        return pd.DataFrame(summary_data)
    
    def export_results(self, output_dir: str = "output"):
        """Export all results to Excel and CSV files."""
        os.makedirs(output_dir, exist_ok=True)
        
        # Export summary report
        summary_df = self.create_summary_report()
        summary_df.to_excel(os.path.join(output_dir, 'frequency_sweep_summary.xlsx'), index=False)
        summary_df.to_csv(os.path.join(output_dir, 'frequency_sweep_summary.csv'), index=False)
        
        # Export detailed results for each frequency
        for freq, result in self.results.items():
            if 'error' not in result:
                # Export transition analysis
                if not result['transition_analysis'].empty:
                    filename = f"{freq.replace('MHz', '')}_transition_analysis"
                    result['transition_analysis'].to_excel(
                        os.path.join(output_dir, f'{filename}.xlsx'), index=False
                    )
                    result['transition_analysis'].to_csv(
                        os.path.join(output_dir, f'{filename}.csv'), index=False
                    )
                
                # Export filtered raw data
                if not result['raw_data'].empty:
                    filename = f"{freq.replace('MHz', '')}_filtered_data"
                    result['raw_data'].to_excel(
                        os.path.join(output_dir, f'{filename}.xlsx'), index=False
                    )
                    result['raw_data'].to_csv(
                        os.path.join(output_dir, f'{filename}.csv'), index=False
                    )
        
        print(f"Results exported to {output_dir} directory")
    
    def create_visualizations(self, output_dir: str = "output"):
        """Create visualizations of the analysis results."""
        os.makedirs(output_dir, exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8')
        
        # 1. Duration comparison across frequencies
        freq_durations = []
        freq_labels = []
        
        for freq, result in self.results.items():
            if 'error' not in result:
                freq_durations.append(result['duration_summary']['total_duration'])
                freq_labels.append(freq)
        
        if freq_durations:
            plt.figure(figsize=(10, 6))
            plt.bar(freq_labels, freq_durations, color='skyblue', alpha=0.7)
            plt.title('Total Duration by Frequency Sweep')
            plt.xlabel('Frequency')
            plt.ylabel('Total Duration')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'duration_by_frequency.png'), dpi=300)
            plt.show()
        
        # 2. Transition analysis for each frequency
        for freq, result in self.results.items():
            if 'error' not in result and not result['transition_analysis'].empty:
                plt.figure(figsize=(12, 8))
                
                # Get top 10 transitions by total duration
                trans_df = result['transition_analysis'].copy()
                if 'DURATION_sum' in trans_df.columns:
                    top_transitions = trans_df.nlargest(10, 'DURATION_sum')
                    
                    plt.barh(top_transitions['TRANSITION'], top_transitions['DURATION_sum'])
                    plt.title(f'Top 10 Transitions by Total Duration - {freq}')
                    plt.xlabel('Total Duration')
                    plt.ylabel('Transition')
                    plt.tight_layout()
                    plt.savefig(os.path.join(output_dir, f'{freq}_top_transitions.png'), dpi=300)
                    plt.show()

def main():
    """Main function to run the simulation analysis."""
    analyzer = SimulationAnalyzer()
    
    # Run the analysis
    results = analyzer.run_analysis()
    
    # Print summary
    print("\n" + "="*60)
    print("ANALYSIS SUMMARY")
    print("="*60)
    
    summary_df = analyzer.create_summary_report()
    print(summary_df.to_string(index=False))
    
    # Export results
    analyzer.export_results()
    
    # Create visualizations
    analyzer.create_visualizations()
    
    print("\nAnalysis complete! Check the 'output' directory for detailed results.")

if __name__ == "__main__":
    main()