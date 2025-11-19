# Enhanced Hardware Projector v2.0 - User Guide

## Overview
The Enhanced Hardware Projector provides a configurable system for projecting performance from current hardware to future hardware generations. The system supports multiple calculation approaches and is designed to be generic enough to work with any current→future hardware transition.

## Key Features

### 1. **Configurable Execution Options**
- **Single Approach**: Run one specific calculation method
- **Multiple Approaches**: Run selected combination of approaches  
- **All Approaches**: Run all three approaches for comprehensive comparison

### 2. **Generic Hardware Improvement Framework**
- **Current Hardware**: Any baseline hardware (default: PVC - Ponte Vecchio)
- **Future Hardware**: Any target hardware (default: JGS - Jaguar Shores)
- **Configurable Parameters**: All improvement factors can be customized

### 3. **Three Calculation Approaches**

#### Option A: Hardware-Calibrated Approach
- Uses measured hardware performance (TTFT/TPOT) as baseline
- Applies frequency scaling and hardware improvements
- Best for: When you have reliable hardware measurements

#### Option B: Pure Simulation Approach  
- Uses simulation duration data directly
- Converts simulation time to real-world performance
- Best for: When simulation accurately models workload

#### Option C: Hybrid Correlation Approach
- Combines hardware measurements with simulation resource analysis
- Provides balanced accuracy using both data sources
- Best for: Maximum accuracy with comprehensive data

## Configuration System

### Hardware Configuration
```json
{
  "hardware_settings": {
    "current_hardware": {
      "name": "PVC",
      "description": "Ponte Vecchio Current Generation",
      "baseline_measurements": {
        "ttft_ms": 8336,
        "tpot_ms": 53.46,
        "baseline_frequency": 1600
      }
    },
    "future_hardware": {
      "name": "JGS", 
      "description": "Next Generation Hardware",
      "improvement_factors": {
        "xecore_compute": {
          "value": 0.375,
          "description": "35-40% faster compute",
          "configurable": true
        }
      }
    }
  }
}
```

### Execution Configuration
```json
{
  "calculation_settings": {
    "enabled_approaches": [
      "hardware_calibrated",
      "pure_simulation", 
      "hybrid_correlation"
    ],
    "execution_options": {
      "run_single_approach": false,
      "run_all_approaches": true,
      "default_single_approach": "hybrid_correlation"
    }
  }
}
```

## Usage Examples

### 1. Interactive Mode (Recommended)
```bash
python interactive_projector.py
```
**Features:**
- Menu-driven interface
- Real-time parameter configuration
- Scenario analysis (conservative/optimistic)
- Results visualization

### 2. Command Line Mode
```bash
# Run single approach
python interactive_projector.py --approach hw --config my_config.json

# Run all approaches
python interactive_projector.py --approach all

# Run scenario analysis
python interactive_projector.py --scenario conservative
```

### 3. Programmatic Usage
```python
from enhanced_hardware_projector import EnhancedHardwareProjector, CalculationApproach

# Initialize with custom config
projector = EnhancedHardwareProjector("my_config.json")

# Run specific approaches
approaches = [CalculationApproach.HYBRID_CORRELATION]
results = projector.calculate_projections(approaches)

# Generate analysis
analysis = projector.generate_comparison_analysis(results)
```

## Configuration Parameters

### Hardware Improvement Factors

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `xecore_compute` | Time Ratio | Compute performance improvement | 0.375 (37.5% faster) |
| `hbm_bandwidth` | Multiplier | Memory bandwidth improvement | 6.5 (6.5x faster) |
| `fabrication_process` | Time Ratio | Process node improvement | 0.75 (25% faster) |
| `communication.bandwidth` | Multiplier | Communication throughput | 12.5 (12.5x faster) |
| `communication.latency` | Multiplier | Communication latency reduction | 150 (150x lower) |

### Resource Distribution Settings

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ex_u1_split.memory_copy` | Fraction of ex_u1 that is memory | 0.30 |
| `ex_u1_split.communication` | Fraction of ex_u1 that is communication | 0.70 |
| `fallback_weights.compute` | Compute weight when no detailed data | 0.4 |
| `fallback_weights.memory` | Memory weight when no detailed data | 0.3 |
| `fallback_weights.communication` | Communication weight when no detailed data | 0.3 |

## Approach Selection Guide

### When to Use Each Approach

1. **Hardware-Calibrated** 
   - ✅ Have reliable hardware measurements
   - ✅ Want conservative estimates
   - ❌ Simulation doesn't match real workload

2. **Pure Simulation**
   - ✅ Simulation accurately models workload  
   - ✅ Want to use actual simulation runtime
   - ❌ Hardware measurements are unreliable

3. **Hybrid Correlation**  
   - ✅ Have both hardware and simulation data
   - ✅ Want maximum accuracy
   - ✅ Need balanced approach

### Typical Result Ranges

Based on PVC→JGS projections:
- **Hardware-Calibrated**: 5.10 - 16.99 tok/s
- **Pure Simulation**: 11.71 - 39.02 tok/s  
- **Hybrid Correlation**: 5.10 - 16.99 tok/s (similar to hardware-calibrated)

## Multi-GPU Scaling

The system supports automatic scaling to multi-GPU configurations:
- **8T Configuration**: 4 GPUs × 2 tiles = 8 tiles
- **16T Configuration**: 8 GPUs × 2 tiles = 16 tiles  
- **144T Configuration**: 72 GPUs × 2 tiles = 144 tiles

Scaling efficiency can be configured per workload type.

## Output Files

### Generated Reports
1. **enhanced_hardware_projections.csv** - Detailed projection data
2. **projection_analysis.json** - Comparative analysis results
3. **projection_config.json** - Configuration used for run
4. **visualization plots** - Performance comparison charts

### Analysis Features
- Statistical summary (mean, min, max, std dev)
- Approach comparison and recommendations
- Frequency trend analysis
- Multi-GPU scaling projections

## Customization Examples

### Example 1: Conservative Hardware Estimates
```json
{
  "alternative_hardware_scenarios": {
    "conservative_estimates": {
      "xecore_compute": 0.5,
      "hbm_bandwidth": 4.0,
      "fabrication_process": 0.85,
      "communication_bandwidth": 8.0,
      "communication_latency": 100.0
    }
  }
}
```

### Example 2: Different Hardware Transition
```json
{
  "hardware_settings": {
    "current_hardware": {
      "name": "Gen1",
      "description": "First Generation Architecture"
    },
    "future_hardware": {
      "name": "Gen2", 
      "description": "Second Generation Architecture",
      "improvement_factors": {
        "compute_cores": {"value": 0.6},
        "memory_bandwidth": {"value": 4.0},
        "interconnect": {"value": 8.0}
      }
    }
  }
}
```

## Troubleshooting

### Common Issues

1. **No Simulation Data Found**
   ```
   Solution: Run universal_analyzer.py first to generate master_summary.csv
   ```

2. **Configuration File Not Found**
   ```
   Solution: Use hardware_projection_config.json template or create custom config
   ```

3. **Approach Returns No Results**
   ```
   Solution: Check that simulation data contains GT resources with DURATION
   ```

4. **Large Variance Between Approaches**
   ```
   This is expected - use hybrid approach for balanced results
   ```

## Best Practices

1. **Always run all approaches initially** to understand result ranges
2. **Use hybrid approach for production estimates** 
3. **Validate configuration parameters** against known hardware specs
4. **Save custom configurations** for reproducible analyses
5. **Review analysis recommendations** for approach selection guidance

## Advanced Features

### Custom Correlation Factors
Adjust simulation-to-reality correlation:
```json
{
  "simulation_correlation": {
    "correlation_factor": 2.311296913926394e-06,
    "calibration_method": "hardware_baseline"
  }
}
```

### Multi-Scenario Analysis
Run multiple scenarios in batch:
```python
scenarios = ["conservative", "optimistic", "current"]
for scenario in scenarios:
    results = run_scenario_analysis(scenario)
```

### Integration with CI/CD
```bash
# Automated testing with different configurations
python interactive_projector.py --approach all --config test_config.json
```

This enhanced system provides maximum flexibility while maintaining ease of use for both interactive exploration and automated analysis workflows.