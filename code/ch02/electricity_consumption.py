import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Embedded electricity data from CSV file
electricity_data = [
    {"Date": "12/14", "Peak feedin": 0, "Offpeak feedin": 0, "consumption": 492},
    {"Date": "02/15", "Peak feedin": 0, "Offpeak feedin": 0, "consumption": 782},
    {"Date": "04/15", "Peak feedin": 0, "Offpeak feedin": 0, "consumption": 678},
    {"Date": "06/15", "Peak feedin": 0, "Offpeak feedin": 0, "consumption": 365},
    {"Date": "08/15", "Peak feedin": 0, "Offpeak feedin": 0, "consumption": 7},
    {"Date": "10/15", "Peak feedin": 0, "Offpeak feedin": 0, "consumption": 366},
    {"Date": "12/15", "Peak feedin": 0, "Offpeak feedin": 0, "consumption": 558},
    {"Date": "02/16", "Peak feedin": 0, "Offpeak feedin": 0, "consumption": 751},
    {"Date": "04/16", "Peak feedin": 0, "Offpeak feedin": 0, "consumption": 697},
    {"Date": "06/16", "Peak feedin": 0, "Offpeak feedin": 0, "consumption": 499},
    {"Date": "08/16", "Peak feedin": 0, "Offpeak feedin": 0, "consumption": 639},
    {"Date": "10/16", "Peak feedin": 0, "Offpeak feedin": 0, "consumption": 769},
    {"Date": "12/16", "Peak feedin": 0, "Offpeak feedin": 0, "consumption": 475},
    {"Date": "02/17", "Peak feedin": 0, "Offpeak feedin": 0, "consumption": 281},
    {"Date": "04/17", "Peak feedin": 0, "Offpeak feedin": 0, "consumption": 623},
    {"Date": "06/17", "Peak feedin": 0, "Offpeak feedin": 0, "consumption": 541},
    {"Date": "08/17", "Peak feedin": 0, "Offpeak feedin": 0, "consumption": 779},
    {"Date": "10/17", "Peak feedin": 0, "Offpeak feedin": 0, "consumption": 508},
    {"Date": "12/17", "Peak feedin": 0, "Offpeak feedin": 0, "consumption": 466},
    {"Date": "02/18", "Peak feedin": 0, "Offpeak feedin": 0, "consumption": 380},
    {"Date": "04/18", "Peak feedin": 0, "Offpeak feedin": 0, "consumption": 682},
    {"Date": "06/18", "Peak feedin": 0, "Offpeak feedin": 0, "consumption": 528},
    {"Date": "08/18", "Peak feedin": 0, "Offpeak feedin": 0, "consumption": 576},
    {"Date": "10/18", "Peak feedin": 0, "Offpeak feedin": 0, "consumption": 532},
    {"Date": "12/18", "Peak feedin": 0, "Offpeak feedin": 0, "consumption": 495},
    {"Date": "02/19", "Peak feedin": 0, "Offpeak feedin": 0, "consumption": 654},
    {"Date": "04/19", "Peak feedin": 0, "Offpeak feedin": 0, "consumption": 583},
    {"Date": "06/19", "Peak feedin": 0, "Offpeak feedin": 0, "consumption": 564},
    {"Date": "08/19", "Peak feedin": 0, "Offpeak feedin": 0, "consumption": 584},
    {"Date": "10/19", "Peak feedin": 0, "Offpeak feedin": 0, "consumption": 427},
    {"Date": "12/19", "Peak feedin": 0, "Offpeak feedin": 0, "consumption": 591},
    {"Date": "02/20", "Peak feedin": 0, "Offpeak feedin": 0, "consumption": 721},
    {"Date": "04/20", "Peak feedin": 0, "Offpeak feedin": 0, "consumption": 740},
    {"Date": "06/20", "Peak feedin": 0, "Offpeak feedin": 0, "consumption": 636},
    {"Date": "08/20", "Peak feedin": 0, "Offpeak feedin": 0, "consumption": 604},
    {"Date": "10/20", "Peak feedin": 0, "Offpeak feedin": 0, "consumption": 524},
    {"Date": "12/20", "Peak feedin": 0, "Offpeak feedin": 0, "consumption": 536},
    {"Date": "02/21", "Peak feedin": 149.76, "Offpeak feedin": 955.17, "consumption": 357.04},
    {"Date": "04/21", "Peak feedin": 150.91, "Offpeak feedin": 1028.95, "consumption": 577.76},
    {"Date": "06/21", "Peak feedin": 37.9, "Offpeak feedin": 566.19, "consumption": 612.16},
    {"Date": "08/21", "Peak feedin": 35.5, "Offpeak feedin": 369.7, "consumption": 1298.17},
    {"Date": "09/21", "Peak feedin": 34.7, "Offpeak feedin": 374.87, "consumption": 1303.47},
    {"Date": "10/21", "Peak feedin": 105.27, "Offpeak feedin": 890.92, "consumption": 679.84},
    {"Date": "12/21", "Peak feedin": 141.06, "Offpeak feedin": 1129.43, "consumption": 480.89},
    {"Date": "02/22", "Peak feedin": 115.01, "Offpeak feedin": 883.83, "consumption": 771.63},
    {"Date": "04/22", "Peak feedin": 50.98, "Offpeak feedin": 628.25, "consumption": 731.73},
    {"Date": "08/22", "Peak feedin": 18.7, "Offpeak feedin": 307.94, "consumption": 1066.89},
    {"Date": "10/22", "Peak feedin": 55.69, "Offpeak feedin": 663.01, "consumption": 762.82},
    {"Date": "12/22", "Peak feedin": 97.67, "Offpeak feedin": 921.53, "consumption": 442.21},
    {"Date": "02/23", "Peak feedin": 129.24, "Offpeak feedin": 1057.19, "consumption": 633.55},
    {"Date": "04/23", "Peak feedin": 66.84, "Offpeak feedin": 751.9, "consumption": 617.33},
    {"Date": "06/23", "Peak feedin": 15.09, "Offpeak feedin": 355.58, "consumption": 987.48},
    {"Date": "08/23", "Peak feedin": 14.06, "Offpeak feedin": 292.6, "consumption": 1244.14},
    {"Date": "10/23", "Peak feedin": 47.4, "Offpeak feedin": 635.17, "consumption": 712.65},
    {"Date": "12/23", "Peak feedin": 86.57, "Offpeak feedin": 952.45, "consumption": 547.53},
    {"Date": "02/24", "Peak feedin": 84.84, "Offpeak feedin": 855.87, "consumption": 776.42},
    {"Date": "04/24", "Peak feedin": 61.15, "Offpeak feedin": 768.32, "consumption": 788.48},
    {"Date": "06/24", "Peak feedin": 15.6, "Offpeak feedin": 380.31, "consumption": 991.43},
    {"Date": "08/24", "Peak feedin": 13.1, "Offpeak feedin": 238.06, "consumption": 1251.0},
    {"Date": "10/24", "Peak feedin": 50.3, "Offpeak feedin": 682.93, "consumption": 791.48},
    {"Date": "12/24", "Peak feedin": 83.96, "Offpeak feedin": 858.64, "consumption": 633.5},
    {"Date": "02/25", "Peak feedin": 148.27, "Offpeak feedin": 930.17, "consumption": 812.7}
]

# Embedded gas data from CSV file
gas_data = [
    {"Date": "12/14", "Units": 1460},
    {"Date": "03/15", "Units": 773},
    {"Date": "06/15", "Units": 1056},
    {"Date": "09/15", "Units": 0},
    {"Date": "12/15", "Units": 854},
    {"Date": "03/16", "Units": 605},
    {"Date": "06/16", "Units": 968},
    {"Date": "09/16", "Units": 769},
    {"Date": "12/16", "Units": 1291},
    {"Date": "03/17", "Units": 385},
    {"Date": "06/17", "Units": 984},
    {"Date": "09/17", "Units": 1582},
    {"Date": "12/17", "Units": 1286},
    {"Date": "03/18", "Units": 395},
    {"Date": "06/18", "Units": 955},
    {"Date": "09/18", "Units": 1450},
    {"Date": "12/18", "Units": 1391},
    {"Date": "03/19", "Units": 984},
    {"Date": "06/19", "Units": 1074},
    {"Date": "09/19", "Units": 1677},
    {"Date": "12/19", "Units": 1097},
    {"Date": "03/20", "Units": 983},
    {"Date": "06/20", "Units": 1248},
    {"Date": "09/20", "Units": 1638},
    {"Date": "12/20", "Units": 1278},
    {"Date": "02/21", "Units": 32},
    {"Date": "05/21", "Units": 42},
    {"Date": "08/21", "Units": 95},
    {"Date": "11/21", "Units": 64},
    {"Date": "03/22", "Units": 63},
    {"Date": "05/22", "Units": 52},
    {"Date": "08/22", "Units": 63},
    {"Date": "11/22", "Units": 63},
    {"Date": "02/23", "Units": 63},
    {"Date": "05/23", "Units": 53},
    {"Date": "08/23", "Units": 74},
    {"Date": "11/23", "Units": 74},
    {"Date": "02/24", "Units": 54},
    {"Date": "05/24", "Units": 75},
    {"Date": "08/24", "Units": 64},
    {"Date": "11/24", "Units": 64}
]

# Create DataFrames from embedded data
df_elec = pd.DataFrame(electricity_data)
df_gas = pd.DataFrame(gas_data)

# Calculate total production for electricity data
df_elec['total_production'] = df_elec['Peak feedin'] + df_elec['Offpeak feedin']
df_elec['date_index'] = range(len(df_elec))

# Create a mapping function to align gas data with electricity data timeline
def find_matching_elec_index(gas_date):
    """Find the closest electricity data index for a given gas date"""
    # Simple matching based on date strings - could be improved with proper date parsing
    for i, elec_date in enumerate(df_elec['Date']):
        if gas_date == elec_date:
            return i
    # If no exact match, find closest
    gas_parts = gas_date.split('/')
    gas_month, gas_year = int(gas_parts[0]), int(gas_parts[1])

    best_match = 0
    min_diff = float('inf')

    for i, elec_date in enumerate(df_elec['Date']):
        elec_parts = elec_date.split('/')
        elec_month, elec_year = int(elec_parts[0]), int(elec_parts[1])

        year_diff = abs(gas_year - elec_year)
        month_diff = abs(gas_month - elec_month)
        total_diff = year_diff * 12 + month_diff

        if total_diff < min_diff:
            min_diff = total_diff
            best_match = i

    return best_match

# Add corresponding electricity index to gas data
df_gas['elec_index'] = df_gas['Date'].apply(find_matching_elec_index)

# Create the plot with dual y-axes
fig, ax1 = plt.subplots(figsize=(16, 10))

# Plot electricity data on the primary (left) y-axis
line1 = ax1.plot(df_elec['date_index'], df_elec['consumption'],
                 linestyle='-',
                 marker='o', linewidth=3, markersize=9,
                 #color='#E74C3C', markerfacecolor='#E74C3C',
                 color='#C5E9EF', markerfacecolor='#C5E9EF',
                 label='Electricity Consumption', alpha=1)

line2 = ax1.plot(df_elec['date_index'], df_elec['total_production'],
                 linestyle='--',
                 marker='s', linewidth=3, markersize=9,
                 #color='#27AE60', markerfacecolor='#27AE60',
                 color='#80C21D', markerfacecolor='#80C21D',
                 label='Solar Production', alpha=1)

# Customize the primary y-axis (electricity)
ax1.set_xlabel('Date', fontsize=12, fontweight='normal')
ax1.set_ylabel('Electricity (kWh)', fontsize=12, fontweight='normal', color='black')
ax1.tick_params(axis='y', labelcolor='black')

# Create secondary y-axis for gas data
ax2 = ax1.twinx()

# Plot gas data on the secondary (right) y-axis
line3 = ax2.plot(df_gas['elec_index'], df_gas['Units'],
                 linestyle=':',
                 marker='^', linewidth=3, markersize=9,
                 #color='#2E86AB', markerfacecolor='#2E86AB',
                 color='#491F6E', markerfacecolor='#491F6E',
                 label='Gas Consumption', alpha=1)

# Customize the secondary y-axis (gas)
ax2.set_ylabel('Gas (Units)', fontsize=12, fontweight='normal', color='black')
ax2.tick_params(axis='y', labelcolor='black')

# Set x-axis ticks to show every 8th date for better readability
tick_positions = range(0, len(df_elec), 8)
tick_labels = [df_elec.iloc[i]['Date'] for i in tick_positions]
ax1.set_xticks(tick_positions)
ax1.set_xticklabels(tick_labels, rotation=45)

# Set title
plt.title('Electricity vs Gas Consumption and Solar Production Over Time',
          fontsize=16, fontweight='normal', pad=20)

# Combine legends from both axes
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=11, framealpha=0.9)

# Add grid for better readability
plt.grid(True, alpha=0.3, linestyle='--')

# Add some styling
plt.tight_layout()


# Show the plot
plt.show()
#plt.savefig('electricity_consumption.png', dpi=300, bbox_inches='tight')