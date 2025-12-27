"""
OSeMOSYS Data File Generator for Israeli Energy Sector
Time Horizon: 2015-2050
Generates input YAML files using tz-osemosys format from Excel demand data
"""

import pandas as pd
import numpy as np
import yaml
from pathlib import Path
try:
    from tz.osemosys import Model
    TZ_OSEMOSYS_AVAILABLE = True
except ImportError:
    TZ_OSEMOSYS_AVAILABLE = False
    print("Warning: tz-osemosys not installed. Install with: pip install tz-osemosys")

class OSeMOSYSIsraelDataGenerator:
    def __init__(self, excel_demand_file, output_dir='osemosys_data', yaml_format=True):
        """
        Initialize the generator
        
        Parameters:
        -----------
        excel_demand_file : str
            Path to Excel file containing useful energy demand data
        output_dir : str
            Directory to save output YAML files
        yaml_format : bool
            If True, generate YAML files (tz-osemosys format). If False, generate CSV files.
        """
        self.excel_file = excel_demand_file
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.yaml_format = yaml_format
        
        # Time settings
        self.start_year = 2015
        self.end_year = 2050
        self.years = list(range(self.start_year, self.end_year + 1))
        
        # Define model structure
        self.define_sets()
        
    def define_sets(self):
        """Define all sets (commodities, technologies, etc.)"""
        
        # Region
        self.regions = ['ISRAEL']
        
        # Time slices (simplified: 3 seasons x 2 daily periods = 6 slices)
        self.timeslices = [
            'SUMMER_DAY', 'SUMMER_NIGHT',
            'WINTER_DAY', 'WINTER_NIGHT',
            'INTERMEDIATE_DAY', 'INTERMEDIATE_NIGHT'
        ]
        
        # Commodities
        self.commodities = {
            'primary': [
                'NaturalGas', 'Coal', 'CrudeOil', 'SolarRadiation', 
                'Wind', 'Biomass'
            ],
            'secondary': [
                'Electricity', 'Diesel', 'Gasoline', 'LPG', 'JetFuel', 
                'HeavyFuelOil', 'SAF', 'Methanol', 'Ammonia', 
                'SyntheticDiesel', 'Biodiesel', 'Ethanol', 'Hydrogen'
            ],
            'useful': [
                'ElecResidential', 'ElecCommercial', 'ElecIndustrial',
                'ElecWater', 'ElecAgriculture', 
                'TransportPrivate', 'TransportPublic', 'TransportFreight',
                'TransportAgriculture', 'TransportHeavyEquip',
                'HeatCoolResidential', 'HeatCoolCommercial', 'IndustrialHeat'
            ]
        }
        
        # All commodities flat list
        self.all_commodities = (
            self.commodities['primary'] + 
            self.commodities['secondary'] + 
            self.commodities['useful']
        )
        
        # Technologies
        self.technologies = {
            'import': [
                'IMP_CrudeOil', 'IMP_NaturalGas', 'IMP_Coal', 'IMP_Hydrogen',
                'IMP_SAF', 'IMP_Methanol', 'IMP_Ethanol', 'IMP_Ammonia',
                'IMP_Biodiesel', 'IMP_SyntheticDiesel'
            ],
            'extraction': [
                'MIN_NaturalGas_Domestic'
            ],
            'power_generation': [
                'PWR_NGCC', 'PWR_NGCC_CCS', 'PWR_OCGT', 'PWR_OCGT_CCS',
                'PWR_NatGas_Steam', 'PWR_Coal', 'PWR_Solar_Utility',
                'PWR_Solar_Rooftop_Res', 'PWR_Solar_Rooftop_Com',
                'PWR_Wind_Onshore', 'PWR_CSP_Storage', 'PWR_WTE_Incinerator',
                'PWR_WTE_Biodigester', 'PWR_Nuclear_SMR', 'PWR_Hydrogen_CCGT'
            ],
            'storage': [
                'STO_Battery', 'STO_Pumped_Hydro'
            ],
            'transmission': [
                'TRN_Electricity'
            ],
            'refining': [
                'REF_Oil', 'REF_Biodiesel', 'REF_Ethanol', 'REF_SAF',
                'REF_SyntheticDiesel', 'REF_Methanol', 'REF_Ammonia'
            ],
            'hydrogen': [
                'H2_Electrolyzer_Green', 'H2_Blue_NatGas_CCS'
            ],
            'distribution': [
                'DST_Diesel', 'DST_Gasoline', 'DST_LPG', 
                'DST_JetFuel', 'DST_Hydrogen'
            ],
            'transport_private': [
                'TRA_Car_Gasoline', 'TRA_Car_Diesel', 'TRA_Car_Hybrid',
                'TRA_Car_BEV', 'TRA_Car_H2'
            ],
            'transport_public': [
                'TRA_Bus_Diesel', 'TRA_Bus_CNG', 'TRA_Bus_Electric',
                'TRA_Bus_H2', 'TRA_LightRail_Electric', 'TRA_Metro_Electric'
            ],
            'transport_rail': [
                'TRA_Rail_Passenger_Electric', 'TRA_Rail_Freight_Diesel'
            ],
            'transport_freight': [
                'TRA_Truck_Diesel', 'TRA_Truck_Electric', 'TRA_Truck_H2'
            ],
            'transport_agriculture': [
                'TRA_AgVehicle_Diesel', 'TRA_AgVehicle_Electric'
            ],
            'transport_heavy': [
                'TRA_HeavyEquip_Diesel', 'TRA_HeavyEquip_Electric'
            ],
            'heating_cooling': [
                'HC_HeatPump_AC_Electric', 'HC_GasBoiler', 
                'HC_SolarWaterHeater', 'HC_DistrictCooling'
            ],
            'demand': [
                'DMD_ElecResidential', 'DMD_ElecCommercial', 'DMD_ElecIndustrial',
                'DMD_ElecWater', 'DMD_ElecAgriculture',
                'DMD_TransportPrivate', 'DMD_TransportPublic', 'DMD_TransportFreight',
                'DMD_TransportAgriculture', 'DMD_TransportHeavyEquip',
                'DMD_HeatCoolResidential', 'DMD_HeatCoolCommercial',
                'DMD_IndustrialHeat'
            ]
        }
        
        # All technologies flat list
        self.all_technologies = []
        for tech_list in self.technologies.values():
            self.all_technologies.extend(tech_list)
    
    def load_demand_data(self):
        """Load demand data from Excel file"""
        print("Loading demand data from Excel...")
        
        # Expected sheet names matching useful energy demands
        demand_sheets = {
            'ElecResidential': 'DMD_ElecResidential',
            'ElecCommercial': 'DMD_ElecCommercial',
            'ElecIndustrial': 'DMD_ElecIndustrial',
            'ElecWater': 'DMD_ElecWater',
            'ElecAgriculture': 'DMD_ElecAgriculture',
            'TransportPrivate': 'DMD_TransportPrivate',
            'TransportPublic': 'DMD_TransportPublic',
            'TransportFreight': 'DMD_TransportFreight',
            'TransportAgriculture': 'DMD_TransportAgriculture',
            'TransportHeavyEquip': 'DMD_TransportHeavyEquip',
            'HeatCoolResidential': 'DMD_HeatCoolResidential',
            'HeatCoolCommercial': 'DMD_HeatCoolCommercial',
            'IndustrialHeat': 'DMD_IndustrialHeat'
        }
        
        self.demand_data = {}
        
        try:
            excel_file = pd.ExcelFile(self.excel_file)
            
            for sheet_name, tech_name in demand_sheets.items():
                if sheet_name in excel_file.sheet_names:
                    df = pd.read_excel(excel_file, sheet_name=sheet_name)
                    # Assume format: Year, Timeslice columns or just Year with annual values
                    self.demand_data[tech_name] = df
                    print(f"  Loaded: {sheet_name}")
                else:
                    print(f"  Warning: Sheet '{sheet_name}' not found. Will use default values.")
                    self.demand_data[tech_name] = self.create_default_demand(tech_name)
                    
        except FileNotFoundError:
            print(f"Excel file not found. Creating template with default values...")
            for tech_name in demand_sheets.values():
                self.demand_data[tech_name] = self.create_default_demand(tech_name)
    
    def create_default_demand(self, tech_name):
        """Create default demand data for missing sheets"""
        # Simple growth assumption: 2% annual growth
        base_demand = 1000  # PJ
        data = []
        for year in self.years:
            growth_factor = (1.02) ** (year - self.start_year)
            data.append({'Year': year, 'AnnualDemand': base_demand * growth_factor})
        return pd.DataFrame(data)
    
    def generate_sets_file(self):
        """Generate SETS.csv file or populate YAML model structure"""
        if self.yaml_format:
            # Build YAML model structure
            self.model_data['model']['regions'] = [{'id': r} for r in self.regions]
            self.model_data['model']['commodities'] = [{'id': f} for f in self.all_commodities]
            self.model_data['model']['technologies'] = [{'id': t} for t in self.all_technologies]
            self.model_data['model']['time_slices'] = [{'id': ts} for ts in self.timeslices]
            self.model_data['model']['emissions'] = [{'id': e} for e in ['CO2', 'NOx', 'SOx', 'PM25']]
            print("Sets defined in YAML model structure")
        else:
            # Original CSV generation
            sets_data = []
            
            # REGION
            for r in self.regions:
                sets_data.append({'SET': 'REGION', 'VALUE': r})
            
            # TECHNOLOGY
            for t in self.all_technologies:
                sets_data.append({'SET': 'TECHNOLOGY', 'VALUE': t})
            
            # FUEL (commodities)
            for f in self.all_commodities:
                sets_data.append({'SET': 'FUEL', 'VALUE': f})
            
            # TIMESLICE
            for ts in self.timeslices:
                sets_data.append({'SET': 'TIMESLICE', 'VALUE': ts})
            
            # YEAR
            for y in self.years:
                sets_data.append({'SET': 'YEAR', 'VALUE': y})
            
            # MODE_OF_OPERATION (simplified: 1 mode per technology)
            sets_data.append({'SET': 'MODE_OF_OPERATION', 'VALUE': 1})
            
            # EMISSION (CO2, other pollutants)
            for e in ['CO2', 'NOx', 'SOx', 'PM25']:
                sets_data.append({'SET': 'EMISSION', 'VALUE': e})
            
            df = pd.DataFrame(sets_data)
            output_file = self.output_dir / 'SETS.csv'
            df.to_csv(output_file, index=False)
            print(f"Generated: {output_file}")
    
    def generate_specified_annual_demand(self):
        """Generate SpecifiedAnnualDemand.csv"""
        data = []
        
        for tech_name, demand_df in self.demand_data.items():
            # Extract the useful energy commodity from demand technology
            # DMD_ElecResidential -> ElecResidential
            fuel = tech_name.replace('DMD_', '')
            
            for _, row in demand_df.iterrows():
                year = int(row['Year'])
                demand = row.get('AnnualDemand', 1000)  # Default if not found
                
                data.append({
                    'REGION': 'ISRAEL',
                    'FUEL': fuel,
                    'YEAR': year,
                    'VALUE': demand
                })
        
        df = pd.DataFrame(data)
        output_file = self.output_dir / 'SpecifiedAnnualDemand.csv'
        df.to_csv(output_file, index=False)
        print(f"Generated: {output_file}")
    
    def generate_capacity_factor(self):
        """Generate CapacityFactor.csv"""
        data = []
        
        # Define capacity factors by technology type
        cf_map = {
            'PWR_Solar_Utility': 0.20,
            'PWR_Solar_Rooftop_Res': 0.18,
            'PWR_Solar_Rooftop_Com': 0.19,
            'PWR_Wind_Onshore': 0.25,
            'PWR_CSP_Storage': 0.45,
            'PWR_NGCC': 0.85,
            'PWR_NGCC_CCS': 0.80,
            'PWR_OCGT': 0.20,
            'PWR_OCGT_CCS': 0.20,
            'PWR_NatGas_Steam': 0.75,
            'PWR_Coal': 0.80,
            'PWR_WTE_Incinerator': 0.85,
            'PWR_WTE_Biodigester': 0.90,
            'PWR_Nuclear_SMR': 0.90,
            'PWR_Hydrogen_CCGT': 0.85
        }
        
        for tech, cf in cf_map.items():
            for year in self.years:
                for ts in self.timeslices:
                    # Adjust CF by timeslice for solar/wind
                    cf_adj = cf
                    if 'Solar' in tech:
                        if 'NIGHT' in ts:
                            cf_adj = 0.0
                        elif 'DAY' in ts:
                            cf_adj = cf * 1.5  # Higher during day
                    
                    data.append({
                        'REGION': 'ISRAEL',
                        'TECHNOLOGY': tech,
                        'TIMESLICE': ts,
                        'YEAR': year,
                        'VALUE': cf_adj
                    })
        
        df = pd.DataFrame(data)
        output_file = self.output_dir / 'CapacityFactor.csv'
        df.to_csv(output_file, index=False)
        print(f"Generated: {output_file}")
    
    def generate_input_activity_ratio(self):
        """Generate InputActivityRatio.csv"""
        data = []
        
        # Define input-output relationships (technology: {input_fuel: ratio})
        # Mode of operation = 1 for all
        
        input_ratios = {
            # Power generation (input fuel per PJ electricity output)
            'PWR_NGCC': {'NaturalGas': 1.75},
            'PWR_NGCC_CCS': {'NaturalGas': 2.0},
            'PWR_OCGT': {'NaturalGas': 2.5},
            'PWR_OCGT_CCS': {'NaturalGas': 2.8},
            'PWR_NatGas_Steam': {'NaturalGas': 2.2},
            'PWR_Coal': {'Coal': 2.5},
            'PWR_Solar_Utility': {'SolarRadiation': 1.0},
            'PWR_Solar_Rooftop_Res': {'SolarRadiation': 1.0},
            'PWR_Solar_Rooftop_Com': {'SolarRadiation': 1.0},
            'PWR_Wind_Onshore': {'Wind': 1.0},
            'PWR_CSP_Storage': {'SolarRadiation': 1.3},
            'PWR_WTE_Incinerator': {'Biomass': 3.0},
            'PWR_WTE_Biodigester': {'Biomass': 2.0},
            'PWR_Nuclear_SMR': {'NaturalGas': 0.01},  # Placeholder
            'PWR_Hydrogen_CCGT': {'Hydrogen': 2.0},
            
            # Transmission
            'TRN_Electricity': {'Electricity': 1.02},  # 2% losses
            
            # Oil refining
            'REF_Oil': {'CrudeOil': 1.05},
            
            # Hydrogen production
            'H2_Electrolyzer_Green': {'Electricity': 1.5},
            'H2_Blue_NatGas_CCS': {'NaturalGas': 1.8},
            
            # Synthetic fuel production
            'REF_Biodiesel': {'Biomass': 1.3, 'Electricity': 0.1},
            'REF_Ethanol': {'Biomass': 1.4, 'Electricity': 0.1},
            'REF_SAF': {'Hydrogen': 1.5, 'Electricity': 0.2},
            'REF_SyntheticDiesel': {'Hydrogen': 1.4, 'Electricity': 0.2},
            'REF_Methanol': {'Hydrogen': 1.3, 'Electricity': 0.15},
            'REF_Ammonia': {'Hydrogen': 1.2, 'Electricity': 0.15},
            
            # Distribution (minimal losses)
            'DST_Diesel': {'Diesel': 1.01},
            'DST_Gasoline': {'Gasoline': 1.01},
            'DST_LPG': {'LPG': 1.01},
            'DST_JetFuel': {'JetFuel': 1.01},
            'DST_Hydrogen': {'Hydrogen': 1.05},
            
            # Transport - Private vehicles
            'TRA_Car_Gasoline': {'Gasoline': 1.0},
            'TRA_Car_Diesel': {'Diesel': 1.0},
            'TRA_Car_Hybrid': {'Gasoline': 0.7, 'Electricity': 0.2},
            'TRA_Car_BEV': {'Electricity': 1.0},
            'TRA_Car_H2': {'Hydrogen': 1.0},
            
            # Transport - Public
            'TRA_Bus_Diesel': {'Diesel': 1.0},
            'TRA_Bus_CNG': {'NaturalGas': 1.0},
            'TRA_Bus_Electric': {'Electricity': 1.0},
            'TRA_Bus_H2': {'Hydrogen': 1.0},
            'TRA_LightRail_Electric': {'Electricity': 1.0},
            'TRA_Metro_Electric': {'Electricity': 1.0},
            
            # Transport - Rail
            'TRA_Rail_Passenger_Electric': {'Electricity': 1.0},
            'TRA_Rail_Freight_Diesel': {'Diesel': 1.0},
            
            # Transport - Freight
            'TRA_Truck_Diesel': {'Diesel': 1.0},
            'TRA_Truck_Electric': {'Electricity': 1.0},
            'TRA_Truck_H2': {'Hydrogen': 1.0},
            
            # Transport - Agriculture
            'TRA_AgVehicle_Diesel': {'Diesel': 1.0},
            'TRA_AgVehicle_Electric': {'Electricity': 1.0},
            
            # Transport - Heavy Equipment
            'TRA_HeavyEquip_Diesel': {'Diesel': 1.0},
            'TRA_HeavyEquip_Electric': {'Electricity': 1.0},
            
            # Heating & Cooling
            'HC_HeatPump_AC_Electric': {'Electricity': 1.0},
            'HC_GasBoiler': {'NaturalGas': 1.1},
            'HC_SolarWaterHeater': {'SolarRadiation': 1.0, 'Electricity': 0.1},
            'HC_DistrictCooling': {'Electricity': 1.2},
        }
        
        for tech, inputs in input_ratios.items():
            for fuel, ratio in inputs.items():
                for year in self.years:
                    data.append({
                        'REGION': 'ISRAEL',
                        'TECHNOLOGY': tech,
                        'FUEL': fuel,
                        'MODE_OF_OPERATION': 1,
                        'YEAR': year,
                        'VALUE': ratio
                    })
        
        df = pd.DataFrame(data)
        output_file = self.output_dir / 'InputActivityRatio.csv'
        df.to_csv(output_file, index=False)
        print(f"Generated: {output_file}")
    
    def generate_output_activity_ratio(self):
        """Generate OutputActivityRatio.csv"""
        data = []
        
        # Define outputs (technology: {output_fuel: ratio})
        output_ratios = {
            # Imports produce their respective fuels
            'IMP_CrudeOil': {'CrudeOil': 1.0},
            'IMP_NaturalGas': {'NaturalGas': 1.0},
            'IMP_Coal': {'Coal': 1.0},
            'IMP_Hydrogen': {'Hydrogen': 1.0},
            'IMP_SAF': {'SAF': 1.0},
            'IMP_Methanol': {'Methanol': 1.0},
            'IMP_Ethanol': {'Ethanol': 1.0},
            'IMP_Ammonia': {'Ammonia': 1.0},
            'IMP_Biodiesel': {'Biodiesel': 1.0},
            'IMP_SyntheticDiesel': {'SyntheticDiesel': 1.0},
            
            # Domestic extraction
            'MIN_NaturalGas_Domestic': {'NaturalGas': 1.0},
            
            # Power generation produces electricity
            'PWR_NGCC': {'Electricity': 1.0},
            'PWR_NGCC_CCS': {'Electricity': 1.0},
            'PWR_OCGT': {'Electricity': 1.0},
            'PWR_OCGT_CCS': {'Electricity': 1.0},
            'PWR_NatGas_Steam': {'Electricity': 1.0},
            'PWR_Coal': {'Electricity': 1.0},
            'PWR_Solar_Utility': {'Electricity': 1.0},
            'PWR_Solar_Rooftop_Res': {'Electricity': 1.0},
            'PWR_Solar_Rooftop_Com': {'Electricity': 1.0},
            'PWR_Wind_Onshore': {'Electricity': 1.0},
            'PWR_CSP_Storage': {'Electricity': 1.0},
            'PWR_WTE_Incinerator': {'Electricity': 1.0},
            'PWR_WTE_Biodigester': {'Electricity': 1.0},
            'PWR_Nuclear_SMR': {'Electricity': 1.0},
            'PWR_Hydrogen_CCGT': {'Electricity': 1.0},
            
            # Transmission
            'TRN_Electricity': {'Electricity': 1.0},
            
            # Oil refining produces multiple fuels
            'REF_Oil': {'Diesel': 0.35, 'Gasoline': 0.25, 'JetFuel': 0.15, 
                       'LPG': 0.10, 'HeavyFuelOil': 0.10},
            
            # Hydrogen production
            'H2_Electrolyzer_Green': {'Hydrogen': 1.0},
            'H2_Blue_NatGas_CCS': {'Hydrogen': 1.0},
            
            # Synthetic fuel production
            'REF_Biodiesel': {'Biodiesel': 1.0},
            'REF_Ethanol': {'Ethanol': 1.0},
            'REF_SAF': {'SAF': 1.0},
            'REF_SyntheticDiesel': {'SyntheticDiesel': 1.0},
            'REF_Methanol': {'Methanol': 1.0},
            'REF_Ammonia': {'Ammonia': 1.0},
            
            # Distribution
            'DST_Diesel': {'Diesel': 1.0},
            'DST_Gasoline': {'Gasoline': 1.0},
            'DST_LPG': {'LPG': 1.0},
            'DST_JetFuel': {'JetFuel': 1.0},
            'DST_Hydrogen': {'Hydrogen': 1.0},
            
            # Transport produces useful energy
            'TRA_Car_Gasoline': {'TransportPrivate': 1.0},
            'TRA_Car_Diesel': {'TransportPrivate': 1.0},
            'TRA_Car_Hybrid': {'TransportPrivate': 1.0},
            'TRA_Car_BEV': {'TransportPrivate': 1.0},
            'TRA_Car_H2': {'TransportPrivate': 1.0},
            
            'TRA_Bus_Diesel': {'TransportPublic': 1.0},
            'TRA_Bus_CNG': {'TransportPublic': 1.0},
            'TRA_Bus_Electric': {'TransportPublic': 1.0},
            'TRA_Bus_H2': {'TransportPublic': 1.0},
            'TRA_LightRail_Electric': {'TransportPublic': 1.0},
            'TRA_Metro_Electric': {'TransportPublic': 1.0},
            
            'TRA_Rail_Passenger_Electric': {'TransportPublic': 1.0},
            'TRA_Rail_Freight_Diesel': {'TransportFreight': 1.0},
            
            'TRA_Truck_Diesel': {'TransportFreight': 1.0},
            'TRA_Truck_Electric': {'TransportFreight': 1.0},
            'TRA_Truck_H2': {'TransportFreight': 1.0},
            
            'TRA_AgVehicle_Diesel': {'TransportAgriculture': 1.0},
            'TRA_AgVehicle_Electric': {'TransportAgriculture': 1.0},
            
            'TRA_HeavyEquip_Diesel': {'TransportHeavyEquip': 1.0},
            'TRA_HeavyEquip_Electric': {'TransportHeavyEquip': 1.0},
            
            # Heating & Cooling
            'HC_HeatPump_AC_Electric': {'HeatCoolResidential': 0.5, 'HeatCoolCommercial': 0.5},
            'HC_GasBoiler': {'HeatCoolResidential': 0.5, 'HeatCoolCommercial': 0.5},
            'HC_SolarWaterHeater': {'HeatCoolResidential': 1.0},
            'HC_DistrictCooling': {'HeatCoolCommercial': 1.0},
        }
        
        for tech, outputs in output_ratios.items():
            for fuel, ratio in outputs.items():
                for year in self.years:
                    data.append({
                        'REGION': 'ISRAEL',
                        'TECHNOLOGY': tech,
                        'FUEL': fuel,
                        'MODE_OF_OPERATION': 1,
                        'YEAR': year,
                        'VALUE': ratio
                    })
        
        df = pd.DataFrame(data)
        output_file = self.output_dir / 'OutputActivityRatio.csv'
        df.to_csv(output_file, index=False)
        print(f"Generated: {output_file}")
    
    def generate_capital_cost(self):
        """Generate CapitalCost.csv (investment costs)"""
        data = []
        
        # Capital costs in M$/GW or M$/PJ capacity
        # These are illustrative values - should be updated with real data
        capital_costs = {
            'PWR_NGCC': 900,
            'PWR_NGCC_CCS': 1500,
            'PWR_OCGT': 600,
            'PWR_OCGT_CCS': 1000,
            'PWR_NatGas_Steam': 1000,
            'PWR_Coal': 2000,
            'PWR_Solar_Utility': 800,
            'PWR_Solar_Rooftop_Res': 1200,
            'PWR_Solar_Rooftop_Com': 1000,
            'PWR_Wind_Onshore': 1400,
            'PWR_CSP_Storage': 5000,
            'PWR_WTE_Incinerator': 3500,
            'PWR_WTE_Biodigester': 2500,
            'PWR_Nuclear_SMR': 6000,
            'PWR_Hydrogen_CCGT': 1200,
            'STO_Battery': 400,
            'STO_Pumped_Hydro': 2000,
            'H2_Electrolyzer_Green': 1000,
            'H2_Blue_NatGas_CCS': 1500,
            'TRA_Car_BEV': 35,
            'TRA_Car_H2': 50,
            'TRA_Bus_Electric': 300,
            'TRA_Bus_H2': 400,
            'TRA_Truck_Electric': 200,
            'TRA_Truck_H2': 300,
        }
        
        for tech, cost in capital_costs.items():
            for year in self.years:
                # Apply technology learning (cost reduction over time)
                cost_year = cost * (0.98 ** (year - self.start_year))
                data.append({
                    'REGION': 'ISRAEL',
                    'TECHNOLOGY': tech,
                    'YEAR': year,
                    'VALUE': cost_year
                })
        
        df = pd.DataFrame(data)
        output_file = self.output_dir / 'CapitalCost.csv'
        df.to_csv(output_file, index=False)
        print(f"Generated: {output_file}")
    
    def generate_fixed_cost(self):
        """Generate FixedCost.csv (annual O&M costs)"""
        data = []
        
        # Fixed O&M costs (% of capital cost per year)
        fixed_costs = {
            'PWR_NGCC': 20,
            'PWR_Solar_Utility': 15,
            'PWR_Wind_Onshore': 25,
            'PWR_Nuclear_SMR': 80,
        }
        
        for tech, cost in fixed_costs.items():
            for year in self.years:
                data.append({
                    'REGION': 'ISRAEL',
                    'TECHNOLOGY': tech,
                    'YEAR': year,
                    'VALUE': cost
                })
        
        df = pd.DataFrame(data)
        output_file = self.output_dir / 'FixedCost.csv'
        df.to_csv(output_file, index=False)
        print(f"Generated: {output_file}")
    
    def generate_variable_cost(self):
        """Generate VariableCost.csv (per PJ produced)"""
        data = []
        
        # Variable costs including fuel costs ($/PJ)
        variable_costs = {
            'IMP_CrudeOil': 15000,
            'IMP_NaturalGas': 8000,
            'IMP_Coal': 3000,
            'IMP_Hydrogen': 50000,
            'PWR_NGCC': 500,
            'PWR_Coal': 800,
            'PWR_Solar_Utility': 10,
            'PWR_Wind_Onshore': 15,
        }
        
        for tech, cost in variable_costs.items():
            for year in self.years:
                data.append({
                    'REGION': 'ISRAEL',
                    'TECHNOLOGY': tech,
                    'MODE_OF_OPERATION': 1,
                    'YEAR': year,
                    'VALUE': cost
                })
        
        df = pd.DataFrame(data)
        output_file = self.output_dir / 'VariableCost.csv'
        df.to_csv(output_file, index=False)
        print(f"Generated: {output_file}")
    
    def generate_emission_activity_ratio(self):
        """Generate EmissionActivityRatio.csv"""
        data = []
        
        # CO2 emissions (tonnes CO2 per PJ)
        emission_ratios = {
            'PWR_NGCC': {'CO2': 56000},
            'PWR_NGCC_CCS': {'CO2': 5600},  # 90% capture
            'PWR_OCGT': {'CO2': 58000},
            'PWR_OCGT_CCS': {'CO2': 5800},
            'PWR_NatGas_Steam': {'CO2': 57000},
            'PWR_Coal': {'CO2': 95000},
            'TRA_Car_Gasoline': {'CO2': 69000},
            'TRA_Car_Diesel': {'CO2': 74000},
            'TRA_Truck_Diesel': {'CO2': 74000},
        }
        
        for tech, emissions in emission_ratios.items():
            for emission, ratio in emissions.items():
                for year in self.years:
                    data.append({
                        'REGION': 'ISRAEL',
                        'TECHNOLOGY': tech,
                        'EMISSION': emission,
                        'MODE_OF_OPERATION': 1,
                        'YEAR': year,
                        'VALUE': ratio
                    })
        
        df = pd.DataFrame(data)
        output_file = self.output_dir / 'EmissionActivityRatio.csv'
        df.to_csv(output_file, index=False)
        print(f"Generated: {output_file}")
    
    def generate_residual_capacity(self):
        """Generate ResidualCapacity.csv (existing capacity in base year)"""
        data = []
        
        # Existing capacity in 2015 (GW for power, appropriate units for others)
        residual_capacity = {
            'PWR_NGCC': 8.0,
            'PWR_Coal': 5.0,
            'PWR_Solar_Utility': 0.5,
            'PWR_Wind_Onshore': 0.1,
        }
        
        for tech, capacity in residual_capacity.items():
            data.append({
                'REGION': 'ISRAEL',
                'TECHNOLOGY': tech,
                'YEAR': self.start_year,
                'VALUE': capacity
            })
        
        df = pd.DataFrame(data)
        output_file = self.output_dir / 'ResidualCapacity.csv'
        df.to_csv(output_file, index=False)
        print(f"Generated: {output_file}")
    
    def build_yaml_model(self):
        """Build complete YAML model structure for tz-osemosys"""
        if not self.yaml_format:
            return
        
        print("Building YAML model structure...")
        
        # Initialize model structure
        model = {
            'id': 'israel_energy_model',
            'time_definition': {
                'start_year': self.start_year,
                'end_year': self.end_year,
                'years': self.years
            },
            'regions': [{'id': r} for r in self.regions],
            'commodities': [{'id': f} for f in self.all_commodities],
            'time_slices': [{'id': ts} for ts in self.timeslices],
            'emissions': [{'id': e} for e in ['CO2', 'NOx', 'SOx', 'PM25']],
            'technologies': []
        }
        
        # Build technology definitions with parameters
        self._add_technologies_to_yaml(model)
        
        # Add demand specifications
        self._add_demand_to_yaml(model)
        
        self.model_data = {'model': model}
    
    def _add_technologies_to_yaml(self, model):
        """Add technology definitions with all parameters to YAML model"""
        # Define all parameter mappings (same as CSV generation)
        cf_map = {
            'PWR_Solar_Utility': 0.20,
            'PWR_Solar_Rooftop_Res': 0.18,
            'PWR_Solar_Rooftop_Com': 0.19,
            'PWR_Wind_Onshore': 0.25,
            'PWR_CSP_Storage': 0.45,
            'PWR_NGCC': 0.85,
            'PWR_NGCC_CCS': 0.80,
            'PWR_OCGT': 0.20,
            'PWR_OCGT_CCS': 0.20,
            'PWR_NatGas_Steam': 0.75,
            'PWR_Coal': 0.80,
            'PWR_WTE_Incinerator': 0.85,
            'PWR_WTE_Biodigester': 0.90,
            'PWR_Nuclear_SMR': 0.90,
            'PWR_Hydrogen_CCGT': 0.85
        }
        
        capital_costs = {
            'PWR_NGCC': 900,
            'PWR_NGCC_CCS': 1500,
            'PWR_OCGT': 600,
            'PWR_OCGT_CCS': 1000,
            'PWR_NatGas_Steam': 1000,
            'PWR_Coal': 2000,
            'PWR_Solar_Utility': 800,
            'PWR_Solar_Rooftop_Res': 1200,
            'PWR_Solar_Rooftop_Com': 1000,
            'PWR_Wind_Onshore': 1400,
            'PWR_CSP_Storage': 5000,
            'PWR_WTE_Incinerator': 3500,
            'PWR_WTE_Biodigester': 2500,
            'PWR_Nuclear_SMR': 6000,
            'PWR_Hydrogen_CCGT': 1200,
            'STO_Battery': 400,
            'STO_Pumped_Hydro': 2000,
            'H2_Electrolyzer_Green': 1000,
            'H2_Blue_NatGas_CCS': 1500,
            'TRA_Car_BEV': 35,
            'TRA_Car_H2': 50,
            'TRA_Bus_Electric': 300,
            'TRA_Bus_H2': 400,
            'TRA_Truck_Electric': 200,
            'TRA_Truck_H2': 300,
        }
        
        fixed_costs = {
            'PWR_NGCC': 20,
            'PWR_Solar_Utility': 15,
            'PWR_Wind_Onshore': 25,
            'PWR_Nuclear_SMR': 80,
        }
        
        variable_costs = {
            'IMP_CrudeOil': 15000,
            'IMP_NaturalGas': 8000,
            'IMP_Coal': 3000,
            'IMP_Hydrogen': 50000,
            'PWR_NGCC': 500,
            'PWR_Coal': 800,
            'PWR_Solar_Utility': 10,
            'PWR_Wind_Onshore': 15,
        }
        
        residual_capacity = {
            'PWR_NGCC': 8.0,
            'PWR_Coal': 5.0,
            'PWR_Solar_Utility': 0.5,
            'PWR_Wind_Onshore': 0.1,
        }
        
        input_ratios = {
            'PWR_NGCC': {'NaturalGas': 1.75},
            'PWR_NGCC_CCS': {'NaturalGas': 2.0},
            'PWR_OCGT': {'NaturalGas': 2.5},
            'PWR_OCGT_CCS': {'NaturalGas': 2.8},
            'PWR_NatGas_Steam': {'NaturalGas': 2.2},
            'PWR_Coal': {'Coal': 2.5},
            'PWR_Solar_Utility': {'SolarRadiation': 1.0},
            'PWR_Solar_Rooftop_Res': {'SolarRadiation': 1.0},
            'PWR_Solar_Rooftop_Com': {'SolarRadiation': 1.0},
            'PWR_Wind_Onshore': {'Wind': 1.0},
            'PWR_CSP_Storage': {'SolarRadiation': 1.3},
            'PWR_WTE_Incinerator': {'Biomass': 3.0},
            'PWR_WTE_Biodigester': {'Biomass': 2.0},
            'PWR_Nuclear_SMR': {'NaturalGas': 0.01},
            'PWR_Hydrogen_CCGT': {'Hydrogen': 2.0},
            'TRN_Electricity': {'Electricity': 1.02},
            'REF_Oil': {'CrudeOil': 1.05},
            'H2_Electrolyzer_Green': {'Electricity': 1.5},
            'H2_Blue_NatGas_CCS': {'NaturalGas': 1.8},
            'REF_Biodiesel': {'Biomass': 1.3, 'Electricity': 0.1},
            'REF_Ethanol': {'Biomass': 1.4, 'Electricity': 0.1},
            'REF_SAF': {'Hydrogen': 1.5, 'Electricity': 0.2},
            'REF_SyntheticDiesel': {'Hydrogen': 1.4, 'Electricity': 0.2},
            'REF_Methanol': {'Hydrogen': 1.3, 'Electricity': 0.15},
            'REF_Ammonia': {'Hydrogen': 1.2, 'Electricity': 0.15},
            'DST_Diesel': {'Diesel': 1.01},
            'DST_Gasoline': {'Gasoline': 1.01},
            'DST_LPG': {'LPG': 1.01},
            'DST_JetFuel': {'JetFuel': 1.01},
            'DST_Hydrogen': {'Hydrogen': 1.05},
            'TRA_Car_Gasoline': {'Gasoline': 1.0},
            'TRA_Car_Diesel': {'Diesel': 1.0},
            'TRA_Car_Hybrid': {'Gasoline': 0.7, 'Electricity': 0.2},
            'TRA_Car_BEV': {'Electricity': 1.0},
            'TRA_Car_H2': {'Hydrogen': 1.0},
            'TRA_Bus_Diesel': {'Diesel': 1.0},
            'TRA_Bus_CNG': {'NaturalGas': 1.0},
            'TRA_Bus_Electric': {'Electricity': 1.0},
            'TRA_Bus_H2': {'Hydrogen': 1.0},
            'TRA_LightRail_Electric': {'Electricity': 1.0},
            'TRA_Metro_Electric': {'Electricity': 1.0},
            'TRA_Rail_Passenger_Electric': {'Electricity': 1.0},
            'TRA_Rail_Freight_Diesel': {'Diesel': 1.0},
            'TRA_Truck_Diesel': {'Diesel': 1.0},
            'TRA_Truck_Electric': {'Electricity': 1.0},
            'TRA_Truck_H2': {'Hydrogen': 1.0},
            'TRA_AgVehicle_Diesel': {'Diesel': 1.0},
            'TRA_AgVehicle_Electric': {'Electricity': 1.0},
            'TRA_HeavyEquip_Diesel': {'Diesel': 1.0},
            'TRA_HeavyEquip_Electric': {'Electricity': 1.0},
            'HC_HeatPump_AC_Electric': {'Electricity': 1.0},
            'HC_GasBoiler': {'NaturalGas': 1.1},
            'HC_SolarWaterHeater': {'SolarRadiation': 1.0, 'Electricity': 0.1},
            'HC_DistrictCooling': {'Electricity': 1.2},
        }
        
        output_ratios = {
            'IMP_CrudeOil': {'CrudeOil': 1.0},
            'IMP_NaturalGas': {'NaturalGas': 1.0},
            'IMP_Coal': {'Coal': 1.0},
            'IMP_Hydrogen': {'Hydrogen': 1.0},
            'IMP_SAF': {'SAF': 1.0},
            'IMP_Methanol': {'Methanol': 1.0},
            'IMP_Ethanol': {'Ethanol': 1.0},
            'IMP_Ammonia': {'Ammonia': 1.0},
            'IMP_Biodiesel': {'Biodiesel': 1.0},
            'IMP_SyntheticDiesel': {'SyntheticDiesel': 1.0},
            'MIN_NaturalGas_Domestic': {'NaturalGas': 1.0},
            'PWR_NGCC': {'Electricity': 1.0},
            'PWR_NGCC_CCS': {'Electricity': 1.0},
            'PWR_OCGT': {'Electricity': 1.0},
            'PWR_OCGT_CCS': {'Electricity': 1.0},
            'PWR_NatGas_Steam': {'Electricity': 1.0},
            'PWR_Coal': {'Electricity': 1.0},
            'PWR_Solar_Utility': {'Electricity': 1.0},
            'PWR_Solar_Rooftop_Res': {'Electricity': 1.0},
            'PWR_Solar_Rooftop_Com': {'Electricity': 1.0},
            'PWR_Wind_Onshore': {'Electricity': 1.0},
            'PWR_CSP_Storage': {'Electricity': 1.0},
            'PWR_WTE_Incinerator': {'Electricity': 1.0},
            'PWR_WTE_Biodigester': {'Electricity': 1.0},
            'PWR_Nuclear_SMR': {'Electricity': 1.0},
            'PWR_Hydrogen_CCGT': {'Electricity': 1.0},
            'TRN_Electricity': {'Electricity': 1.0},
            'REF_Oil': {'Diesel': 0.35, 'Gasoline': 0.25, 'JetFuel': 0.15, 
                       'LPG': 0.10, 'HeavyFuelOil': 0.10},
            'H2_Electrolyzer_Green': {'Hydrogen': 1.0},
            'H2_Blue_NatGas_CCS': {'Hydrogen': 1.0},
            'REF_Biodiesel': {'Biodiesel': 1.0},
            'REF_Ethanol': {'Ethanol': 1.0},
            'REF_SAF': {'SAF': 1.0},
            'REF_SyntheticDiesel': {'SyntheticDiesel': 1.0},
            'REF_Methanol': {'Methanol': 1.0},
            'REF_Ammonia': {'Ammonia': 1.0},
            'DST_Diesel': {'Diesel': 1.0},
            'DST_Gasoline': {'Gasoline': 1.0},
            'DST_LPG': {'LPG': 1.0},
            'DST_JetFuel': {'JetFuel': 1.0},
            'DST_Hydrogen': {'Hydrogen': 1.0},
            'TRA_Car_Gasoline': {'TransportPrivate': 1.0},
            'TRA_Car_Diesel': {'TransportPrivate': 1.0},
            'TRA_Car_Hybrid': {'TransportPrivate': 1.0},
            'TRA_Car_BEV': {'TransportPrivate': 1.0},
            'TRA_Car_H2': {'TransportPrivate': 1.0},
            'TRA_Bus_Diesel': {'TransportPublic': 1.0},
            'TRA_Bus_CNG': {'TransportPublic': 1.0},
            'TRA_Bus_Electric': {'TransportPublic': 1.0},
            'TRA_Bus_H2': {'TransportPublic': 1.0},
            'TRA_LightRail_Electric': {'TransportPublic': 1.0},
            'TRA_Metro_Electric': {'TransportPublic': 1.0},
            'TRA_Rail_Passenger_Electric': {'TransportPublic': 1.0},
            'TRA_Rail_Freight_Diesel': {'TransportFreight': 1.0},
            'TRA_Truck_Diesel': {'TransportFreight': 1.0},
            'TRA_Truck_Electric': {'TransportFreight': 1.0},
            'TRA_Truck_H2': {'TransportFreight': 1.0},
            'TRA_AgVehicle_Diesel': {'TransportAgriculture': 1.0},
            'TRA_AgVehicle_Electric': {'TransportAgriculture': 1.0},
            'TRA_HeavyEquip_Diesel': {'TransportHeavyEquip': 1.0},
            'TRA_HeavyEquip_Electric': {'TransportHeavyEquip': 1.0},
            'HC_HeatPump_AC_Electric': {'HeatCoolResidential': 0.5, 'HeatCoolCommercial': 0.5},
            'HC_GasBoiler': {'HeatCoolResidential': 0.5, 'HeatCoolCommercial': 0.5},
            'HC_SolarWaterHeater': {'HeatCoolResidential': 1.0},
            'HC_DistrictCooling': {'HeatCoolCommercial': 1.0},
        }
        
        emission_ratios = {
            'PWR_NGCC': {'CO2': 56000},
            'PWR_NGCC_CCS': {'CO2': 5600},
            'PWR_OCGT': {'CO2': 58000},
            'PWR_OCGT_CCS': {'CO2': 5800},
            'PWR_NatGas_Steam': {'CO2': 57000},
            'PWR_Coal': {'CO2': 95000},
            'TRA_Car_Gasoline': {'CO2': 69000},
            'TRA_Car_Diesel': {'CO2': 74000},
            'TRA_Truck_Diesel': {'CO2': 74000},
        }
        
        # Build technology entries
        for tech_id in self.all_technologies:
            tech = {'id': tech_id}
            mode = {'id': 1}
            
            # Capacity factor (use wildcard for years, specific timeslices for solar)
            if tech_id in cf_map:
                cf = cf_map[tech_id]
                if 'Solar' in tech_id:
                    mode['capacity_factor'] = {
                        ts: (cf * 1.5 if 'DAY' in ts else 0.0) 
                        for ts in self.timeslices
                    }
                else:
                    mode['capacity_factor'] = {'*': cf}
            
            # Capital cost (base year, learning curve handled separately)
            if tech_id in capital_costs:
                base_cost = capital_costs[tech_id]
                # For simplicity, use base cost for all years
                # In practice, you might want to specify year-by-year or use expressions
                mode['capex'] = {'*': base_cost}
            
            # Fixed cost
            if tech_id in fixed_costs:
                mode['opex_fixed'] = {'*': fixed_costs[tech_id]}
            
            # Variable cost
            if tech_id in variable_costs:
                mode['opex_variable'] = {'*': variable_costs[tech_id]}
            
            # Input activity ratio
            if tech_id in input_ratios:
                mode['input_activity_ratio'] = {
                    fuel: {'*': ratio} for fuel, ratio in input_ratios[tech_id].items()
                }
            
            # Output activity ratio
            if tech_id in output_ratios:
                mode['output_activity_ratio'] = {
                    fuel: {'*': ratio} for fuel, ratio in output_ratios[tech_id].items()
                }
            
            # Emission activity ratio
            if tech_id in emission_ratios:
                mode['emission_activity_ratio'] = {
                    emission: {'*': ratio} 
                    for emission, ratio in emission_ratios[tech_id].items()
                }
            
            # Residual capacity
            if tech_id in residual_capacity:
                tech['residual_capacity'] = {
                    str(self.start_year): residual_capacity[tech_id]
                }
            
            tech['operating_modes'] = [mode]
            model['technologies'].append(tech)
    
    def _add_demand_to_yaml(self, model):
        """Add demand specifications to YAML model"""
        if not hasattr(self, 'demand_data'):
            return
        
        model['specified_demand'] = []
        
        for tech_name, demand_df in self.demand_data.items():
            fuel = tech_name.replace('DMD_', '')
            
            demand_spec = {
                'region': 'ISRAEL',
                'commodity': fuel,
                'demand': {}
            }
            
            for _, row in demand_df.iterrows():
                year = int(row['Year'])
                demand = row.get('AnnualDemand', 1000)
                demand_spec['demand'][str(year)] = demand
            
            model['specified_demand'].append(demand_spec)
    
    def save_yaml_model(self):
        """Save YAML model to file"""
        if not self.yaml_format or not hasattr(self, 'model_data'):
            return
        
        output_file = self.output_dir / 'israel_energy_model.yaml'
        with open(output_file, 'w') as f:
            yaml.dump(self.model_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        print(f"Generated: {output_file}")
        
        # Also try to load with tz-osemosys if available
        if TZ_OSEMOSYS_AVAILABLE:
            try:
                model = Model.from_yaml(str(output_file))
                print(f"Model successfully loaded with tz-osemosys")
            except Exception as e:
                print(f"Warning: Could not load model with tz-osemosys: {e}")
    
    def generate_all_files(self):
        """Generate all OSeMOSYS input files"""
        print("\n=== Generating OSeMOSYS Input Files for Israel Energy Model ===\n")
        
        self.load_demand_data()
        
        if self.yaml_format:
            # Generate YAML format
            self.build_yaml_model()
            self.save_yaml_model()
        else:
            # Generate CSV format (original)
            self.generate_sets_file()
            self.generate_specified_annual_demand()
            self.generate_capacity_factor()
            self.generate_input_activity_ratio()
            self.generate_output_activity_ratio()
            self.generate_capital_cost()
            self.generate_fixed_cost()
            self.generate_variable_cost()
            self.generate_emission_activity_ratio()
            self.generate_residual_capacity()
        
        print(f"\n=== All files generated in '{self.output_dir}' directory ===")
        print("\nNote: Many parameters use illustrative values and should be updated")
        print("with actual data for Israel's energy sector.")
        if self.yaml_format:
            print("\nYAML format uses wildcards (*) for years where values are constant.")
            print("You can load the model with: Model.from_yaml('israel_energy_model.yaml')")
        else:
            print("\nAdditional files may be needed depending on OSeMOSYS version:")
            print("  - OperationalLife.csv")
            print("  - TotalAnnualMaxCapacity.csv")
            print("  - DiscountRate.csv")
            print("  - DepreciationMethod.csv")
            print("  - And others as per OSeMOSYS documentation")


# Usage Example
if __name__ == "__main__":
    # Initialize generator with YAML format (default)
    generator = OSeMOSYSIsraelDataGenerator(
        excel_demand_file='israel_energy_demand.xlsx',
        output_dir='osemosys_israel_data',
        yaml_format=True  # Set to False for CSV format
    )
    
    # Generate all files
    generator.generate_all_files()
    
    print("\n" + "="*60)
    print("IMPORTANT: Update the following with real data:")
    print("  1. Demand projections in Excel file")
    print("  2. Technology costs (capital, fixed, variable)")
    print("  3. Efficiency parameters (input/output ratios)")
    print("  4. Emission factors")
    print("  5. Capacity factors by timeslice")
    print("  6. Existing capacity (residual capacity)")
    print("  7. Resource potentials and constraints")
    print("="*60)
    print("\nTo use CSV format instead, set yaml_format=False in the generator.")
