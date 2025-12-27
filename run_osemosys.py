"""
Run OSeMOSYS Model for Israel Energy Sector

This script loads the OSeMOSYS model from YAML and solves it.
"""

from pathlib import Path
from tz.osemosys import Model

def run_model(yaml_file=None, solver_name=None):
    """
    Load and solve the OSeMOSYS model
    
    Parameters
    ----------
    yaml_file : str, optional
        Path to YAML model file. Defaults to 'osemosys_data_yaml/israel_energy_model.yaml'
    solver_name : str, optional
        Solver to use (e.g., 'highs', 'cbc', 'glpk'). If None, uses default solver.
    """
    # Default YAML file path
    if yaml_file is None:
        yaml_file = 'osemosys_data_yaml/israel_energy_model.yaml'
    
    yaml_path = Path(yaml_file)
    
    if not yaml_path.exists():
        print(f"Error: YAML file not found: {yaml_path}")
        print("\nPlease run the data generator first:")
        print("  python osemosys_israel.py")
        return None
    
    print(f"Loading model from: {yaml_path}")
    print("=" * 60)
    
    try:
        # Load the model
        model = Model.from_yaml(str(yaml_path))
        print("Model loaded successfully!")
        print(f"Model ID: {model.id}")
        print(f"Time horizon: {model.time_definition.start_year} - {model.time_definition.end_year}")
        print(f"Regions: {[r.id for r in model.regions]}")
        print(f"Technologies: {len(model.technologies)}")
        print(f"Commodities: {len(model.commodities)}")
        
        print("\n" + "=" * 60)
        print("Solving model...")
        print("=" * 60)
        
        # Solve the model with error handling
        try:
            if solver_name:
                print(f"Using solver: {solver_name}")
                model.solve(solver_name=solver_name)
            else:
                print("Using default solver")
                model.solve()
            
            print("\nModel solved successfully!")
            print("=" * 60)
            
        except ImportError as e:
            print(f"\nError: Solver not available - {e}")
            print("\nTroubleshooting:")
            print("  1. Install a solver:")
            print("     pip install highspy  (recommended)")
            print("     or install cbc/glpk separately")
            print("  2. Check that the solver is properly installed")
            raise
            
        except ValueError as e:
            error_msg = str(e).lower()
            if 'solver' in error_msg or 'not found' in error_msg:
                print(f"\nError: Solver '{solver_name}' not found or not available")
                print("\nTroubleshooting:")
                print("  1. Install the solver:")
                if solver_name == 'highs':
                    print("     pip install highspy")
                elif solver_name == 'cbc':
                    print("     Install CBC solver separately")
                elif solver_name == 'glpk':
                    print("     Install GLPK solver separately")
                else:
                    print(f"     Install {solver_name} solver")
                print("  2. Try using a different solver or let the model choose default")
            else:
                print(f"\nError: {e}")
            raise
            
        except RuntimeError as e:
            error_msg = str(e).lower()
            if 'infeasible' in error_msg:
                print(f"\nError: Model is infeasible - {e}")
                print("\nThis means the model constraints cannot be satisfied.")
                print("Possible causes:")
                print("  1. Demand exceeds available capacity")
                print("  2. Conflicting constraints")
                print("  3. Missing or incorrect input data")
                print("  4. Technology parameters that prevent meeting demand")
            elif 'unbounded' in error_msg:
                print(f"\nError: Model is unbounded - {e}")
                print("\nThis means the objective function can be improved indefinitely.")
                print("Possible causes:")
                print("  1. Missing cost parameters")
                print("  2. Missing capacity constraints")
            else:
                print(f"\nError during solving: {e}")
            raise
            
        except Exception as e:
            print(f"\nError: Unexpected error during solving - {e}")
            print(f"Error type: {type(e).__name__}")
            print("\nTroubleshooting:")
            print("  1. Check that the model is properly defined")
            print("  2. Verify all required parameters are present")
            print("  3. Check solver installation and availability")
            print("  4. Review the model YAML file for errors")
            raise
        
        # Display solution summary
        if hasattr(model, 'solution') and model.solution is not None:
            print("\nSolution available. Key variables:")
            print(f"  Available variables: {list(model.solution.data_vars)}")
            
            # Show objective value if available
            if hasattr(model, '_m') and model._m is not None:
                if hasattr(model._m, 'objective') and model._m.objective is not None:
                    try:
                        obj_value = model._m.objective.value()
                        print(f"\nObjective value: {obj_value:,.2f}")
                    except:
                        pass
        
        return model
        
    except Exception as e:
        print(f"\nError: {e}")
        print("\nTroubleshooting:")
        print("  1. Ensure all dependencies are installed: pip install -r requirements.txt")
        print("  2. Check that the YAML file is valid")
        print("  3. Ensure a solver is available (highs, cbc, or glpk)")
        print("     Install with: pip install highspy  (or cbc, or glpk)")
        raise


def view_solution(model, variable_name='NewCapacity'):
    """
    View a specific variable from the solution
    
    Parameters
    ----------
    model : Model
        Solved OSeMOSYS model
    variable_name : str
        Name of variable to view (e.g., 'NewCapacity', 'TotalCapacityAnnual', 'ProductionByTechnologyAnnual')
    """
    if not hasattr(model, 'solution') or model.solution is None:
        print("Model has not been solved yet.")
        return
    
    if variable_name not in model.solution.data_vars:
        print(f"Variable '{variable_name}' not found.")
        print(f"Available variables: {list(model.solution.data_vars)}")
        return
    
    df = model.solution[variable_name].to_dataframe().reset_index()
    print(f"\n{variable_name}:")
    print("=" * 60)
    print(df.to_string())
    return df


def export_solution(model, output_dir='results'):
    """
    Export all solution variables to Excel files
    
    Parameters
    ----------
    model : Model
        Solved OSeMOSYS model
    output_dir : str
        Directory to save Excel files
    """
    if not hasattr(model, 'solution') or model.solution is None:
        print("Model has not been solved yet.")
        return
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    print(f"\nExporting solution to: {output_path}")
    print("=" * 60)
    
    for var_name in model.solution.data_vars:
        df = model.solution[var_name].to_dataframe().reset_index()
        excel_file = output_path / f"{var_name}.xlsx"
        df.to_excel(excel_file, index=False)
        print(f"  Exported: {excel_file}")
    
    print(f"\nAll solution variables exported to {output_path}")


if __name__ == "__main__":
    import sys
    
    # Parse command line arguments
    yaml_file = None
    solver_name = None
    
    if len(sys.argv) > 1:
        yaml_file = sys.argv[1]
    if len(sys.argv) > 2:
        solver_name = sys.argv[2]
    
    # Run the model
    model = run_model(yaml_file=yaml_file, solver_name=solver_name)
    
    if model is not None:
        # Example: View NewCapacity
        print("\n" + "=" * 60)
        print("Example: Viewing NewCapacity variable")
        print("=" * 60)
        view_solution(model, 'NewCapacity')
        
        # Optionally export all results
        print("\n" + "=" * 60)
        export_choice = input("Export all solution variables to Excel? (y/n): ").strip().lower()
        if export_choice == 'y':
            export_solution(model)

