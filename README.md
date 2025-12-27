# OSeMOSYS Israel Energy Model

This project contains an OSeMOSYS energy system model for Israel's energy sector (2015-2050), using the `tz-osemosys` Python package.

## Prerequisites

- Python 3.8 or higher
- Virtual environment (recommended)

## Installation

1. **Create and activate a virtual environment** (if not already done):
```bash
python -m venv env
# On Windows:
env\Scripts\activate
# On Linux/Mac:
source env/bin/activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Install a solver** (required to solve the model):
```bash
# Option 1: HiGHS (recommended, free and fast)
pip install highspy

# Option 2: CBC (free)
# Requires conda or separate installation

# Option 3: GLPK (free)
# Requires separate installation
```

## Quick Start

### Step 1: Generate Input Files

The model input files are generated from a data generator script. If you already have the YAML file (`osemosys_data_yaml/israel_energy_model.yaml`), you can skip this step.

To generate input files:
```bash
python osemosys_israel.py
```

This will create the YAML model file in `osemosys_data_yaml/israel_energy_model.yaml`.

**Note**: The script expects an Excel file `israel_energy_demand.xlsx` with demand data. If this file doesn't exist, it will use default values.

### Step 2: Run the Model

Run the model using the provided script:
```bash
python run_osemosys.py
```

Or specify a custom YAML file and solver:
```bash
python run_osemosys.py osemosys_data_yaml/israel_energy_model.yaml highs
```

### Step 3: View Results

After solving, the script will display:
- Model summary information
- Objective value (total system cost)
- Example output (NewCapacity variable)

You can also export all results to Excel:
```bash
python run_osemosys.py
# When prompted, type 'y' to export results
```

Results will be saved in the `results/` directory as Excel files.

## Using Python Directly

You can also run the model directly in Python:

```python
from tz.osemosys import Model

# Load the model
model = Model.from_yaml('osemosys_data_yaml/israel_energy_model.yaml')

# Solve the model
model.solve(solver_name='highs')  # or 'cbc', 'glpk', or None for default

# View solution variables
print(model.solution.data_vars)  # List all available variables

# Access a specific variable
new_capacity = model.solution['NewCapacity']
print(new_capacity.to_dataframe())

# Export to Excel
new_capacity.to_dataframe().reset_index().to_excel('NewCapacity.xlsx', index=False)
```

## Available Solution Variables

After solving, the model provides various output variables, including:

- `NewCapacity` - New capacity installed by technology and year
- `TotalCapacityAnnual` - Total capacity by technology and year
- `ProductionByTechnologyAnnual` - Annual production by technology
- `ProductionByTechnology` - Production by technology, timeslice, and year
- `UseByTechnology` - Fuel use by technology
- `AnnualEmissions` - Annual emissions by pollutant
- `TotalDiscountedCost` - Total discounted system cost
- And many more...

## Project Structure

```
OSeMOSYS2/
├── osemosys_israel.py              # Data generator script
├── run_osemosys.py                 # Model runner script
├── osemosys_expand_wildcards.py   # CSV wildcard expander utility
├── osemosys_data_yaml/            # YAML input files
│   └── israel_energy_model.yaml   # Main model file
├── osemosys_data_csv/             # CSV input files (alternative format)
├── results/                        # Output directory (created after solving)
├── requirements.txt               # Python dependencies
└── README.md                       # This file
```

## Troubleshooting

### "YAML file not found"
- Run `python osemosys_israel.py` first to generate the input files

### "No solver available"
- Install a solver: `pip install highspy` (recommended)

### "Model validation errors"
- Check that the YAML file is valid
- Ensure all required parameters are defined
- Review the model structure in `osemosys_israel.py`

### "Import errors"
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

## Model Parameters

The model includes:
- **Time horizon**: 2015-2050
- **Region**: Israel
- **Technologies**: Power generation, storage, refining, transport, heating/cooling
- **Commodities**: Primary (natural gas, coal, oil, renewables), secondary (electricity, fuels), and useful energy demands
- **Time slices**: 6 slices (3 seasons × 2 daily periods)

## Updating Model Data

To update the model with real data:

1. **Demand data**: Update `israel_energy_demand.xlsx` with actual demand projections
2. **Technology costs**: Edit cost parameters in `osemosys_israel.py` (capital_costs, fixed_costs, variable_costs)
3. **Efficiency parameters**: Update input/output ratios in `osemosys_israel.py`
4. **Capacity factors**: Modify capacity_factors dictionary
5. **Existing capacity**: Update residual_capacity values

After making changes, regenerate the YAML file:
```bash
python osemosys_israel.py
```

## Additional Resources

- [OSeMOSYS Documentation](https://osemosys.readthedocs.io/)
- [tz-osemosys GitHub](https://github.com/tz-osemosys/tz-osemosys)
- [WILDCARD_USAGE.md](WILDCARD_USAGE.md) - Information about using wildcards in CSV files

## License

[Add your license information here]

