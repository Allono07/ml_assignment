import requests
import pandas as pd
from collections import defaultdict

# Fetch the JSON data from the URL
url = "https://data.covid19india.org/states_daily.json"
response = requests.get(url)
data = response.json()

# Load data into a DataFrame
df = pd.DataFrame(data["states_daily"])

# Convert the date column to datetime
df['date'] = pd.to_datetime(df['dateymd'], format='%Y-%m-%d')


# Function to perform analysis for given start and end dates
def analyze_data(start_date, end_date):
    # Filter data within the date range
    mask = (df['date'] >= start_date) & (df['date'] <= end_date)
    df_filtered = df[mask]

    # Initialize counters
    confirmed_count = defaultdict(int)
    recovered_count = defaultdict(int)
    deceased_count = defaultdict(int)

    # Process the filtered data
    for _, row in df_filtered.iterrows():
        status = row["status"]
        for state, count in row.items():
            if state not in ["date", "dateymd", "status", "tt"]:
                if status == "Confirmed":
                    confirmed_count[state] += int(count)
                elif status == "Recovered":
                    recovered_count[state] += int(count)
                elif status == "Deceased":
                    deceased_count[state] += int(count)

    # Calculate total counts
    total_confirmed = sum(confirmed_count.values())
    total_recovered = sum(recovered_count.values())
    total_deceased = sum(deceased_count.values())

    return total_confirmed, total_recovered, total_deceased, confirmed_count, recovered_count, deceased_count


# Define the date ranges
start_date_1 = '2020-03-14'
end_date_1 = '2020-09-30'

start_date_2 = '2020-03-14'
end_date_2 = '2020-09-05'

# Perform analysis for the first date range
total_confirmed_1, total_recovered_1, total_deceased_1, _, _, _ = analyze_data(start_date_1, end_date_1)

# Perform analysis for the second date range and specific states
_, _, _, confirmed_count_2, recovered_count_2, deceased_count_2 = analyze_data(start_date_2, end_date_2)
delhi_counts = {
    'Confirmed': confirmed_count_2['dl'],
    'Recovered': recovered_count_2['dl'],
    'Deceased': deceased_count_2['dl']
}
karnataka_counts = {
    'Confirmed': confirmed_count_2['ka'],
    'Recovered': recovered_count_2['ka'],
    'Deceased': deceased_count_2['ka']
}
combined_counts = {status: delhi_counts[status] + karnataka_counts[status] for status in delhi_counts}

# Highest and lowest affected states
state_totals = defaultdict(lambda: {'Confirmed': 0, 'Recovered': 0, 'Deceased': 0})
for state in confirmed_count_2.keys():
    state_totals[state]['Confirmed'] = confirmed_count_2[state]
    state_totals[state]['Recovered'] = recovered_count_2[state]
    state_totals[state]['Deceased'] = deceased_count_2[state]

highest_confirmed_state = max(state_totals.items(), key=lambda x: x[1]['Confirmed'])
lowest_confirmed_state = min(state_totals.items(), key=lambda x: x[1]['Confirmed'])

# Find the day with the highest spike in Delhi
delhi_data = df[(df['date'] >= start_date_2) & (df['date'] <= end_date_2)]
delhi_confirmed_spike = \
delhi_data[delhi_data['status'] == 'Confirmed'][['date', 'dl']].astype({'dl': 'int'}).sort_values(by='dl',
                                                                                                  ascending=False).iloc[
    0]
delhi_recovered_spike = \
delhi_data[delhi_data['status'] == 'Recovered'][['date', 'dl']].astype({'dl': 'int'}).sort_values(by='dl',
                                                                                                  ascending=False).iloc[
    0]
delhi_deceased_spike = \
delhi_data[delhi_data['status'] == 'Deceased'][['date', 'dl']].astype({'dl': 'int'}).sort_values(by='dl',
                                                                                                 ascending=False).iloc[
    0]

# Calculate active cases on 05-Sept-2020
active_cases_date = '2020-09-05'
active_mask = (df['date'] == active_cases_date)
active_data = df[active_mask]

active_cases = defaultdict(int)
for _, row in active_data.iterrows():
    status = row["status"]
    for state, count in row.items():
        if state not in ["date", "dateymd", "status", "tt"]:
            if status == "Confirmed":
                active_cases[state] += int(count)
            elif status == "Recovered":
                active_cases[state] -= int(count)
            elif status == "Deceased":
                active_cases[state] -= int(count)

# Print the results
print(f"Total Confirmed (14-Mar-2020 to 30-Sept-2020): {total_confirmed_1}")
print(f"Total Recovered (14-Mar-2020 to 30-Sept-2020): {total_recovered_1}")
print(f"Total Deceased (14-Mar-2020 to 30-Sept-2020): {total_deceased_1}")

print(
    f"Delhi (Confirmed): {delhi_counts['Confirmed']}, Delhi (Recovered): {delhi_counts['Recovered']}, Delhi (Deceased): {delhi_counts['Deceased']}")
print(
    f"Combined Delhi and Karnataka (Confirmed): {combined_counts['Confirmed']}, Combined Delhi and Karnataka (Recovered): {combined_counts['Recovered']}, Combined Delhi and Karnataka (Deceased): {combined_counts['Deceased']}")

print(
    f"Highest Affected State (Confirmed): {highest_confirmed_state[0]}, Count: {highest_confirmed_state[1]['Confirmed']}")
print(
    f"Lowest Affected State (Confirmed): {lowest_confirmed_state[0]}, Count: {lowest_confirmed_state[1]['Confirmed']}")

print(f"Highest spike in Delhi (Confirmed): {delhi_confirmed_spike['date']} with {delhi_confirmed_spike['dl']} cases")
print(f"Highest spike in Delhi (Recovered): {delhi_recovered_spike['date']} with {delhi_recovered_spike['dl']} cases")
print(f"Highest spike in Delhi (Deceased): {delhi_deceased_spike['date']} with {delhi_deceased_spike['dl']} cases")

print(f"Active cases on 05-Sept-2020:")
for state, active in active_cases.items():
    print(f"{state}: {active}")
