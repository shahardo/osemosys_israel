# OSeMOSYS Israel Energy Model - Model Description

## Model Overview

The OSeMOSYS Israel Energy Model is a long-term energy system optimization model covering the period 2015-2050. The model optimizes the least-cost energy system configuration to meet specified energy demands while respecting technical, economic, and environmental constraints.

### Model Characteristics

- **Model ID**: `israel_energy_model`
- **Time Horizon**: 2015-2050 (36 years)
- **Region**: Israel (ISRAEL)
- **Time Slices**: 6 time slices representing seasonal and daily variations
  - SUMMER_DAY, SUMMER_NIGHT
  - WINTER_DAY, WINTER_NIGHT
  - INTERMEDIATE_DAY, INTERMEDIATE_NIGHT
- **Objective Function**: Minimize total discounted system cost
- **Model Type**: Linear Programming (LP) optimization

---

## Parameters

Parameters are input data that define the model's constraints, costs, and technical characteristics. All parameters are specified in the YAML model file.

### Technology Parameters

#### Capacity Parameters

- **`residual_capacity`** (ResidualCapacity)
  - Existing capacity at the start of the model period (GW)
  - Example: PWR_NGCC has 8.0 GW residual capacity in 2015

- **`capacity_factor`** (CapacityFactor)
  - Fraction of installed capacity that can be utilized in each time slice
  - Varies by technology and time slice (e.g., solar has zero capacity factor at night)
  - Units: dimensionless (0-1)
  - Example: PWR_Solar_Utility has 0.20 annual capacity factor, but 0.0 at night

#### Cost Parameters

- **`capex`** (CapitalCost)
  - Capital investment cost per unit of capacity
  - Units: $ million per GW (or equivalent unit for non-power technologies)
  - Example: PWR_NGCC has capex of 900 $mn/GW

- **`opex_fixed`** (FixedCost)
  - Annual fixed operating and maintenance cost per unit of capacity
  - Units: $ million per GW per year
  - Example: PWR_NGCC has fixed cost of 20 $mn/GW/yr

- **`opex_variable`** (VariableCost)
  - Variable operating cost per unit of activity
  - Units: $ million per PJ (or equivalent activity unit)
  - Example: PWR_NGCC has variable cost of 500 $mn/PJ

#### Technical Parameters

- **`input_activity_ratio`** (InputActivityRatio)
  - Amount of input commodity required per unit of technology activity
  - Units: PJ input per PJ output (or equivalent)
  - Example: PWR_NGCC requires 1.75 PJ NaturalGas per PJ Electricity output

- **`output_activity_ratio`** (OutputActivityRatio)
  - Amount of output commodity produced per unit of technology activity
  - Units: PJ output per PJ activity (typically 1.0 for single-output technologies)
  - Example: PWR_NGCC produces 1.0 PJ Electricity per PJ activity

- **`emission_activity_ratio`** (EmissionActivityRatio)
  - Amount of emission produced per unit of technology activity
  - Units: tonnes of emission per PJ activity
  - Example: PWR_NGCC emits 56,000 tonnes CO2 per PJ activity

- **`operating_life`** (OperationalLife)
  - Economic lifetime of the technology
  - Units: years
  - Default: varies by technology type

### Demand Parameters

- **`demand_annual`** (SpecifiedAnnualDemand)
  - Annual demand for useful energy commodities
  - Units: PJ per year
  - Specified by region, commodity, and year
  - Example: ElecResidential demand in 2020

### System Parameters

- **`discount_rate`** (DiscountRate)
  - Social discount rate for cost calculations
  - Units: dimensionless (typically 0.05 = 5%)
  - Default: 0.05 (5%)

- **`depreciation_method`** (DepreciationMethod)
  - Method for calculating depreciation
  - Options: 'sinking-fund' or 'straight-line'
  - Default: 'sinking-fund'

---

## Variables

Variables are the decision variables and outputs from the optimization model. These are calculated by the solver and available in the model solution.

### Capacity Variables

- **`NewCapacity`** (NewCapacity)
  - New capacity installed in each year for each technology
  - Units: GW (or equivalent capacity unit)
  - Dimensions: [region, technology, year]
  - Key output: Shows investment decisions over time

- **`TotalCapacityAnnual`** (TotalCapacityAnnual)
  - Total installed capacity available in each year
  - Units: GW
  - Dimensions: [region, technology, year]
  - Includes both residual and newly installed capacity

- **`TotalCapacity`** (TotalCapacity)
  - Total capacity by technology, time slice, and year
  - Units: GW
  - Dimensions: [region, technology, timeslice, year]

### Activity Variables

- **`ProductionByTechnology`** (ProductionByTechnology)
  - Production by technology, time slice, and year
  - Units: PJ (or equivalent activity unit)
  - Dimensions: [region, technology, timeslice, year]
  - Key output: Shows when and how much each technology operates

- **`ProductionByTechnologyAnnual`** (ProductionByTechnologyAnnual)
  - Annual production aggregated across all time slices
  - Units: PJ per year
  - Dimensions: [region, technology, year]

- **`UseByTechnology`** (UseByTechnology)
  - Commodity use (input) by technology, time slice, and year
  - Units: PJ
  - Dimensions: [region, technology, commodity, timeslice, year]

- **`UseByTechnologyAnnual`** (UseByTechnologyAnnual)
  - Annual commodity use aggregated across time slices
  - Units: PJ per year
  - Dimensions: [region, technology, commodity, year]

### Cost Variables

- **`TotalDiscountedCost`** (TotalDiscountedCost)
  - Total discounted system cost (objective function value)
  - Units: $ million (discounted)
  - Dimensions: [region, year]
  - Sum of all discounted costs over the model period

- **`TotalDiscountedCostByTechnology`** (TotalDiscountedCostByTechnology)
  - Discounted cost by technology
  - Units: $ million
  - Dimensions: [region, technology, year]

- **`CapitalInvestment`** (CapitalInvestment)
  - Annual capital investment by technology
  - Units: $ million
  - Dimensions: [region, technology, year]

- **`OperatingCost`** (OperatingCost)
  - Annual operating cost (fixed + variable) by technology
  - Units: $ million
  - Dimensions: [region, technology, year]

### Emission Variables

- **`AnnualEmissions`** (AnnualEmissions)
  - Annual emissions by pollutant
  - Units: tonnes per year
  - Dimensions: [region, emission, year]
  - Key output: Shows environmental impacts

- **`ProductionByTechnologyAnnual`** (for emission tracking)
  - Used in conjunction with emission activity ratios to calculate emissions

### Other Variables

- **`RateOfActivity`** (RateOfActivity)
  - Activity rate by technology, mode, time slice, and year
  - Units: PJ (or equivalent)
  - Dimensions: [region, technology, mode, timeslice, year]

- **`RateOfTotalActivity`** (RateOfTotalActivity)
  - Total activity rate aggregated across modes
  - Units: PJ
  - Dimensions: [region, technology, timeslice, year]

- **`Demand`** (Demand)
  - Actual demand met (should equal specified demand for useful energy)
  - Units: PJ
  - Dimensions: [region, commodity, timeslice, year]

---

## Commodities

Commodities represent energy carriers and useful energy demands in the model. They are organized into three categories:

### Primary Commodities

Primary commodities are natural resources and raw energy sources:

1. **NaturalGas** - Natural gas (fossil fuel)
2. **Coal** - Coal (fossil fuel)
3. **CrudeOil** - Crude oil (fossil fuel)
4. **SolarRadiation** - Solar radiation (renewable resource)
5. **Wind** - Wind energy (renewable resource)
6. **Biomass** - Biomass (renewable resource)

### Secondary Commodities

Secondary commodities are processed energy carriers and intermediate products:

1. **Electricity** - Electrical energy
2. **Diesel** - Diesel fuel
3. **Gasoline** - Gasoline fuel
4. **LPG** - Liquefied Petroleum Gas
5. **JetFuel** - Aviation jet fuel
6. **HeavyFuelOil** - Heavy fuel oil
7. **SAF** - Sustainable Aviation Fuel
8. **Methanol** - Methanol
9. **Ammonia** - Ammonia
10. **SyntheticDiesel** - Synthetic diesel
11. **Biodiesel** - Biodiesel
12. **Ethanol** - Ethanol
13. **Hydrogen** - Hydrogen

### Useful Energy Commodities

Useful energy commodities represent final energy services demanded by end-users:

#### Electricity Demands
1. **ElecResidential** - Residential electricity demand
2. **ElecCommercial** - Commercial electricity demand
3. **ElecIndustrial** - Industrial electricity demand
4. **ElecWater** - Water sector electricity demand
5. **ElecAgriculture** - Agricultural electricity demand

#### Transport Demands
6. **TransportPrivate** - Private transport services
7. **TransportPublic** - Public transport services
8. **TransportFreight** - Freight transport services
9. **TransportAgriculture** - Agricultural transport services
10. **TransportHeavyEquip** - Heavy equipment transport services

#### Heat/Cooling Demands
11. **HeatCoolResidential** - Residential heating and cooling
12. **HeatCoolCommercial** - Commercial heating and cooling
13. **IndustrialHeat** - Industrial heat demand

---

## Technologies

Technologies are organized into functional categories. Each technology can have multiple operating modes with different characteristics.

### Import Technologies

Technologies that import commodities from outside the system:

1. **IMP_CrudeOil** - Crude oil import
2. **IMP_NaturalGas** - Natural gas import
3. **IMP_Coal** - Coal import
4. **IMP_Hydrogen** - Hydrogen import
5. **IMP_SAF** - Sustainable Aviation Fuel import
6. **IMP_Methanol** - Methanol import
7. **IMP_Ethanol** - Ethanol import
8. **IMP_Ammonia** - Ammonia import
9. **IMP_Biodiesel** - Biodiesel import
10. **IMP_SyntheticDiesel** - Synthetic diesel import

### Extraction Technologies

Technologies that extract primary resources:

1. **MIN_NaturalGas_Domestic** - Domestic natural gas extraction

### Power Generation Technologies

Electricity generation technologies:

#### Fossil Fuel Power
1. **PWR_NGCC** - Natural Gas Combined Cycle (without CCS)
2. **PWR_NGCC_CCS** - Natural Gas Combined Cycle with Carbon Capture and Storage
3. **PWR_OCGT** - Open Cycle Gas Turbine (without CCS)
4. **PWR_OCGT_CCS** - Open Cycle Gas Turbine with CCS
5. **PWR_NatGas_Steam** - Natural Gas Steam Turbine
6. **PWR_Coal** - Coal-fired power plant

#### Renewable Power
7. **PWR_Solar_Utility** - Utility-scale solar PV
8. **PWR_Solar_Rooftop_Res** - Residential rooftop solar PV
9. **PWR_Solar_Rooftop_Com** - Commercial rooftop solar PV
10. **PWR_Wind_Onshore** - Onshore wind power
11. **PWR_CSP_Storage** - Concentrated Solar Power with storage

#### Other Power
12. **PWR_WTE_Incinerator** - Waste-to-energy incinerator
13. **PWR_WTE_Biodigester** - Waste-to-energy biodigester
14. **PWR_Nuclear_SMR** - Small Modular Reactor (nuclear)
15. **PWR_Hydrogen_CCGT** - Hydrogen-fired Combined Cycle Gas Turbine

### Storage Technologies

Energy storage technologies:

1. **STO_Battery** - Battery energy storage
2. **STO_Pumped_Hydro** - Pumped hydro storage

### Transmission Technologies

Energy transmission/distribution:

1. **TRN_Electricity** - Electricity transmission and distribution

### Refining Technologies

Fuel refining and processing:

1. **REF_Oil** - Oil refining (produces diesel, gasoline, jet fuel, LPG, heavy fuel oil)
2. **REF_Biodiesel** - Biodiesel production
3. **REF_Ethanol** - Ethanol production
4. **REF_SAF** - Sustainable Aviation Fuel production
5. **REF_SyntheticDiesel** - Synthetic diesel production
6. **REF_Methanol** - Methanol production
7. **REF_Ammonia** - Ammonia production

### Hydrogen Production Technologies

Hydrogen production:

1. **H2_Electrolyzer_Green** - Green hydrogen via electrolysis
2. **H2_Blue_NatGas_CCS** - Blue hydrogen from natural gas with CCS

### Distribution Technologies

Fuel distribution:

1. **DST_Diesel** - Diesel distribution
2. **DST_Gasoline** - Gasoline distribution
3. **DST_LPG** - LPG distribution
4. **DST_JetFuel** - Jet fuel distribution
5. **DST_Hydrogen** - Hydrogen distribution

### Transport Technologies

#### Private Transport
1. **TRA_Car_Gasoline** - Gasoline passenger car
2. **TRA_Car_Diesel** - Diesel passenger car
3. **TRA_Car_Hybrid** - Hybrid passenger car
4. **TRA_Car_BEV** - Battery electric vehicle (passenger)
5. **TRA_Car_H2** - Hydrogen fuel cell vehicle (passenger)

#### Public Transport
6. **TRA_Bus_Diesel** - Diesel bus
7. **TRA_Bus_CNG** - Compressed Natural Gas bus
8. **TRA_Bus_Electric** - Electric bus
9. **TRA_Bus_H2** - Hydrogen fuel cell bus
10. **TRA_LightRail_Electric** - Light rail (electric)
11. **TRA_Metro_Electric** - Metro/subway (electric)

#### Rail Transport
12. **TRA_Rail_Passenger_Electric** - Electric passenger rail
13. **TRA_Rail_Freight_Diesel** - Diesel freight rail

#### Freight Transport
14. **TRA_Truck_Diesel** - Diesel truck
15. **TRA_Truck_Electric** - Electric truck
16. **TRA_Truck_H2** - Hydrogen fuel cell truck

#### Agricultural Transport
17. **TRA_AgVehicle_Diesel** - Diesel agricultural vehicle
18. **TRA_AgVehicle_Electric** - Electric agricultural vehicle

#### Heavy Equipment
19. **TRA_HeavyEquip_Diesel** - Diesel heavy equipment
20. **TRA_HeavyEquip_Electric** - Electric heavy equipment

### Heating and Cooling Technologies

1. **HC_HeatPump_AC_Electric** - Electric heat pump/air conditioning
2. **HC_GasBoiler** - Natural gas boiler
3. **HC_SolarWaterHeater** - Solar water heater
4. **HC_DistrictCooling** - District cooling system

### Demand Technologies

Technologies representing final energy demand (useful energy):

1. **DMD_ElecResidential** - Residential electricity demand
2. **DMD_ElecCommercial** - Commercial electricity demand
3. **DMD_ElecIndustrial** - Industrial electricity demand
4. **DMD_ElecWater** - Water sector electricity demand
5. **DMD_ElecAgriculture** - Agricultural electricity demand
6. **DMD_TransportPrivate** - Private transport demand
7. **DMD_TransportPublic** - Public transport demand
8. **DMD_TransportFreight** - Freight transport demand
9. **DMD_TransportAgriculture** - Agricultural transport demand
10. **DMD_TransportHeavyEquip** - Heavy equipment transport demand
11. **DMD_HeatCoolResidential** - Residential heating/cooling demand
12. **DMD_HeatCoolCommercial** - Commercial heating/cooling demand
13. **DMD_IndustrialHeat** - Industrial heat demand

---

## Emissions

The model tracks the following emissions:

1. **CO2** - Carbon dioxide
2. **NOx** - Nitrogen oxides
3. **SOx** - Sulfur oxides
4. **PM25** - Particulate matter (2.5 microns)

Emissions are calculated based on technology activity and emission activity ratios.

---

## Model Structure Summary

- **Total Technologies**: ~100+ technologies across all categories
- **Total Commodities**: 29 commodities (6 primary + 13 secondary + 13 useful energy)
- **Time Resolution**: 6 time slices × 36 years = 216 time periods
- **Region**: 1 region (Israel)

---

## Notes

- All cost values are in $ million (mn$)
- Energy values are in Petajoules (PJ)
- Capacity values are in Gigawatts (GW) for power technologies
- The model uses wildcards (*) for parameters that are constant across all years
- Technology learning (cost reduction over time) can be implemented through time-varying parameters
- The model optimizes the least-cost energy system configuration to meet all specified demands

---

## References

- OSeMOSYS Documentation: https://osemosys.readthedocs.io/
- tz-osemosys GitHub: https://github.com/tz-osemosys/tz-osemosys
- Model generator script: `osemosys_israel.py`
- Model input file: `osemosys_data_yaml/israel_energy_model.yaml`

