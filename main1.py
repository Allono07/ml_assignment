import requests

import pandas as pd
from collections import defaultdict

url = "https://data.covid19india.org/states_daily.json"
response = requests.get(url)
data = response.json()

df= pd.DataFrame(data["states_daily"]) #data is present in this object

df['date'] =pd.to_datetime(df['dateymd'],format='%Y-%m-%d')

#function to perform the question answers
def answer_function(start_date,end_date):
    range = (df['date'] >= start_date) & (df['date'] <= end_date)
    df_filtered = df[range]

    confirmed = defaultdict(int)
    recovered = defaultdict(int)
    deceased = defaultdict(int)

    for _, row in df_filtered.iterrows():
        status = row["status"]
        for state,count in row.items():
            if state not in ["date","dateymd","status","tt"]:
                if status == "Confirmed":
                    confirmed[state]+= int(count)
                elif status  == "Recovered":
                    recovered[state]+=int(count)
                elif status == "Deceased":
                    deceased[state]+= int(count)

    total_confirmed = sum(confirmed.values())
    total_recovered = sum(recovered.values())
    total_deceased = sum(deceased.values())

    return  total_confirmed,total_recovered,total_deceased,confirmed,recovered,deceased


# since there are two date range asked in the question, declaring two different date_range:

sDate_1 = '2020-03-14'
eDate_1 = '2020-09-30'

sDate_2 = '2020-03-14'
eDate_2 = '2020-09-05'

total_confirmed_1, total_recovered_1, total_deceased_1, _, _, _ = answer_function(sDate_1,eDate_1)

_, _, _, confirmed_count_2, recovered_count_2, deceased_count_2 = answer_function(sDate_2,eDate_2)

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

state_totals = defaultdict(lambda: {'Confirmed':0,'Recovered':0,'Deceased':0})
for state in confirmed_count_2.keys():
    state_totals[state]['Confirmed'] = confirmed_count_2[state]
    state_totals[state]['Recovered'] = recovered_count_2[state]
    state_totals[state]['Deceased'] = deceased_count_2[state]

highest_confirmed_state = max(state_totals.items(), key=lambda x: x[1]['Confirmed'])
lowest_confirmed_state = min(state_totals.items(), key=lambda x: x[1]['Confirmed'])

delhi_data = df[(df['date'] >= sDate_2) & (df['date'] <= eDate_2)]
delhi_confirmed_spike = delhi_data[delhi_data['status'] == 'Confirmed'][['date', 'dl']].astype({'dl': 'int'}).sort_values(by='dl', ascending=False).iloc[0]
delhi_recovered_spike = delhi_data[delhi_data['status'] == 'Recovered'][['date', 'dl']].astype({'dl': 'int'}).sort_values(by='dl', ascending=False).iloc[0]
delhi_deceased_spike = delhi_data[delhi_data['status'] == 'Deceased'][['date', 'dl']].astype({'dl': 'int'}).sort_values(by='dl', ascending=False).iloc[0]

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


print(f"Answer1 : {total_confirmed_1}")
print(f"Answer 2 {total_recovered_1}")
print(f"Answer 3 {total_deceased_1}")

print(
    f" Answer 3 - Delhi (Confirmed): {delhi_counts['Confirmed']}, Delhi (Recovered): {delhi_counts['Recovered']}, Delhi (Deceased): {delhi_counts['Deceased']}")
print(
    f"Answer 4 - Combined Delhi and Karnataka (Confirmed): {combined_counts['Confirmed']}, Combined Delhi and Karnataka (Recovered): {combined_counts['Recovered']}, Combined Delhi and Karnataka (Deceased): {combined_counts['Deceased']}")

print(
    f"Answer 5- Highest Affected State (Confirmed): {highest_confirmed_state[0]}, Count: {highest_confirmed_state[1]['Confirmed']}")
print(
    f" -Lowest Affected State (Confirmed): {lowest_confirmed_state[0]}, Count: {lowest_confirmed_state[1]['Confirmed']}")


print(f"Answer 6 - Highest spike in Delhi (Confirmed): {delhi_confirmed_spike['date']} with {delhi_confirmed_spike['dl']} cases")
print(f"Highest spike in Delhi (Recovered): {delhi_recovered_spike['date']} with {delhi_recovered_spike['dl']} cases")
print(f"Highest spike in Delhi (Deceased): {delhi_deceased_spike['date']} with {delhi_deceased_spike['dl']} cases")

print(f"Answer 7- Active cases on 05-Sept-2020:")
for state, active in active_cases.items():
    print(f"{state}: {active}")