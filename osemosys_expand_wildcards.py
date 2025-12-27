"""
OSeMOSYS CSV Wildcard Expander
Expands CSV files with wildcard years (*) to explicit year entries
"""

import pandas as pd
import sys
from pathlib import Path

def expand_year_wildcards(input_file, output_file=None, years=None):
    """
    Expand wildcard years (*) in OSeMOSYS CSV files to explicit year entries
    
    Parameters:
    -----------
    input_file : str
        Path to input CSV file (may contain '*' in YEAR column)
    output_file : str, optional
        Path to output CSV file. If None, overwrites input file.
    years : list, optional
        List of years to expand to. If None, reads from SETS.csv
    """
    # Read input file
    df = pd.read_csv(input_file)
    
    # Get years if not provided
    if years is None:
        sets_file = Path(input_file).parent / 'SETS.csv'
        if sets_file.exists():
            sets_df = pd.read_csv(sets_file)
            years = sorted(sets_df[sets_df['SET'] == 'YEAR']['VALUE'].astype(int).tolist())
        else:
            # Default years if SETS.csv not found
            years = list(range(2015, 2051))
            print(f"Warning: SETS.csv not found. Using default years: {years[0]}-{years[-1]}")
    
    # Check if YEAR column exists
    if 'YEAR' not in df.columns:
        print(f"Warning: No YEAR column found in {input_file}. File unchanged.")
        return df
    
    # Find rows with wildcard
    wildcard_rows = df[df['YEAR'].astype(str).str.strip() == '*']
    
    if len(wildcard_rows) == 0:
        print(f"No wildcard entries found in {input_file}. File unchanged.")
        if output_file and output_file != input_file:
            df.to_csv(output_file, index=False)
        return df
    
    print(f"Found {len(wildcard_rows)} rows with wildcard years. Expanding...")
    
    # Remove wildcard rows
    df_no_wildcard = df[df['YEAR'].astype(str).str.strip() != '*']
    
    # Expand wildcard rows
    expanded_rows = []
    for _, row in wildcard_rows.iterrows():
        for year in years:
            new_row = row.copy()
            new_row['YEAR'] = year
            expanded_rows.append(new_row)
    
    # Combine
    expanded_df = pd.concat([df_no_wildcard, pd.DataFrame(expanded_rows)], ignore_index=True)
    
    # Sort by all columns for consistency
    expanded_df = expanded_df.sort_values(by=expanded_df.columns.tolist()).reset_index(drop=True)
    
    # Write output
    if output_file is None:
        output_file = input_file
    
    expanded_df.to_csv(output_file, index=False)
    print(f"Expanded to {len(expanded_df)} rows. Saved to {output_file}")
    
    return expanded_df


def expand_all_files_in_directory(directory, years=None):
    """
    Expand wildcards in all CSV files in a directory
    """
    dir_path = Path(directory)
    csv_files = list(dir_path.glob('*.csv'))
    
    for csv_file in csv_files:
        if csv_file.name == 'SETS.csv':
            continue  # Skip SETS.csv
        print(f"\nProcessing {csv_file.name}...")
        try:
            expand_year_wildcards(csv_file, years=years)
        except Exception as e:
            print(f"Error processing {csv_file.name}: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python osemosys_expand_wildcards.py <input_file.csv> [output_file.csv]")
        print("  python osemosys_expand_wildcards.py --all <directory>")
        print("\nExample:")
        print("  python osemosys_expand_wildcards.py CapacityFactor.csv")
        print("  python osemosys_expand_wildcards.py --all osemosys_israel_data")
        sys.exit(1)
    
    if sys.argv[1] == '--all':
        if len(sys.argv) < 3:
            print("Error: Please specify directory for --all option")
            sys.exit(1)
        expand_all_files_in_directory(sys.argv[2])
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        expand_year_wildcards(input_file, output_file)

