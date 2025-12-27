# Using Wildcards in OSeMOSYS CSV Files

## Overview

Standard OSeMOSYS CSV files **do not support wildcards directly**. However, you can use a compact format with `*` as a wildcard for years, then expand it using the provided script.

## Workflow

1. **Create compact CSV files** with `*` for years that have the same value
2. **Run the expansion script** to generate the full CSV files that OSeMOSYS expects

## Example: CapacityFactor.csv

### Compact Format (with wildcards):
```csv
REGION,TECHNOLOGY,TIMESLICE,YEAR,VALUE
ISRAEL,PWR_Solar_Utility,SUMMER_DAY,*,0.3
ISRAEL,PWR_Solar_Utility,SUMMER_NIGHT,*,0.0
ISRAEL,PWR_Solar_Utility,WINTER_DAY,*,0.3
ISRAEL,PWR_Solar_Utility,WINTER_NIGHT,*,0.0
ISRAEL,PWR_Solar_Utility,INTERMEDIATE_DAY,*,0.3
ISRAEL,PWR_Solar_Utility,INTERMEDIATE_NIGHT,*,0.0
ISRAEL,PWR_NGCC,SUMMER_DAY,*,0.85
ISRAEL,PWR_NGCC,SUMMER_NIGHT,*,0.85
...
```

### Expanded Format (what OSeMOSYS needs):
```csv
REGION,TECHNOLOGY,TIMESLICE,YEAR,VALUE
ISRAEL,PWR_Solar_Utility,SUMMER_DAY,2015,0.3
ISRAEL,PWR_Solar_Utility,SUMMER_DAY,2016,0.3
ISRAEL,PWR_Solar_Utility,SUMMER_DAY,2017,0.3
...
ISRAEL,PWR_Solar_Utility,SUMMER_DAY,2050,0.3
ISRAEL,PWR_Solar_Utility,SUMMER_NIGHT,2015,0.0
...
```

## Usage

### Expand a single file:
```bash
python osemosys_expand_wildcards.py CapacityFactor.csv CapacityFactor_expanded.csv
```

### Expand all CSV files in a directory:
```bash
python osemosys_expand_wildcards.py --all osemosys_israel_data
```

### In Python:
```python
from osemosys_expand_wildcards import expand_year_wildcards

# Expand a single file
expand_year_wildcards('CapacityFactor.csv', 'CapacityFactor_expanded.csv')

# Or expand in-place
expand_year_wildcards('CapacityFactor.csv')
```

## Notes

- The script automatically reads years from `SETS.csv` if available
- If `SETS.csv` is not found, it defaults to years 2015-2050
- You can mix wildcard entries (`*`) with explicit years in the same file
- The script preserves all other columns and data

## Alternative: Use tz-osemosys

For a more powerful solution with native wildcard support, consider using `tz-osemosys` which uses YAML format:

```bash
pip install tz-osemosys
```

This allows you to define parameters in YAML with wildcards, and it generates the CSV files automatically.

