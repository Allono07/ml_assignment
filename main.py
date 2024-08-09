import requests
import matplotlib.pyplot as plt
import pandas as pd
from collections import defaultdict
from sklearn.linear_model import LinearRegression


url = "https://data.covid19india.org/states_daily.json"
response = requests.get(url)
data = response.json()


df = pd.DataFrame(data["states_daily"])
df['date'] = pd.to_datetime(df['dateymd'], format='%Y-%m-%d')


def answer_function(start_date, end_date):
    range_mask = (df['date'] >= start_date) & (df['date'] <= end_date)
    df_filtered = df[range_mask]

    confirmed = defaultdict(int)
    recovered = defaultdict(int)
    deceased = defaultdict(int)

    for _, row in df_filtered.iterrows():
        status = row["status"]
        for state, count in row.items():
            if state not in ["date", "dateymd", "status", "tt"]:
                if status == "Confirmed":
                    confirmed[state] += int(count)
                elif status == "Recovered":
                    recovered[state] += int(count)
                elif status == "Deceased":
                    deceased[state] += int(count)

    total_confirmed = sum(confirmed.values())
    total_recovered = sum(recovered.values())
    total_deceased = sum(deceased.values())

    return total_confirmed, total_recovered, total_deceased, confirmed, recovered, deceased


sDate_1 = '2020-03-14'
eDate_1 = '2020-09-30'

sDate_2 = '2020-03-14'
eDate_2 = '2020-09-05'


total_confirmed_1, total_recovered_1, total_deceased_1, _, _, _ = answer_function(sDate_1, eDate_1)

_, _, _, confirmed_count_2, recovered_count_2, deceased_count_2 = answer_function(sDate_2, eDate_2)

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

state_totals = defaultdict(lambda: {'Confirmed': 0, 'Recovered': 0, 'Deceased': 0})
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

# Print answers to the questions
print(f"Answer 1: Total Confirmed: {total_confirmed_1}, Recovered: {total_recovered_1}, Deceased: {total_deceased_1}")
print(f"Answer 2 - Delhi (Confirmed): {delhi_counts['Confirmed']}, Recovered: {delhi_counts['Recovered']}, Deceased: {delhi_counts['Deceased']}")
print(f"Answer 3 - Combined Delhi and Karnataka (Confirmed): {combined_counts['Confirmed']}, Recovered: {combined_counts['Recovered']}, Deceased: {combined_counts['Deceased']}")
print(f"Answer 4 - Highest Affected State (Confirmed): {highest_confirmed_state[0]}, Count: {highest_confirmed_state[1]['Confirmed']}")
print(f"Answer 5 - Lowest Affected State (Confirmed): {lowest_confirmed_state[0]}, Count: {lowest_confirmed_state[1]['Confirmed']}")
print(f"Answer 6 - Highest spike in Delhi (Confirmed): {delhi_confirmed_spike['date']} with {delhi_confirmed_spike['dl']} cases")
print(f"Highest spike in Delhi (Recovered): {delhi_recovered_spike['date']} with {delhi_recovered_spike['dl']} cases")
print(f"Highest spike in Delhi (Deceased): {delhi_deceased_spike['date']} with {delhi_deceased_spike['dl']} cases")
print(f"Answer 7 - Active cases on 05-Sept-2020:")
for state, active in active_cases.items():
    print(f"{state}: {active}")

# Plotting total cases trend in India
plt.figure(figsize=(14, 8))
plt.stackplot(df['date'].unique(), [total_confirmed_1]*len(df['date'].unique()), [total_recovered_1]*len(df['date'].unique()), [total_deceased_1]*len(df['date'].unique()),
              labels=['Confirmed', 'Recovered', 'Deceased'], colors=['blue', 'yellow', 'red'])
plt.title('Total COVID-19 Cases Trend in India (14-Mar-2020 to 05-Sept-2020)')
plt.ylabel('Number of Cases')
plt.legend(loc='upper left')
plt.show()

# Plotting COVID-19 Cases Trend in Delhi
delhi_confirmed = delhi_data[delhi_data['status'] == 'Confirmed']['dl'].astype(int).cumsum().values
delhi_recovered = delhi_data[delhi_data['status'] == 'Recovered']['dl'].astype(int).cumsum().values
delhi_deceased = delhi_data[delhi_data['status'] == 'Deceased']['dl'].astype(int).cumsum().values

plt.figure(figsize=(14, 8))
plt.stackplot(delhi_data['date'].unique(), delhi_confirmed, delhi_recovered, delhi_deceased,
              labels=['Confirmed', 'Recovered', 'Deceased'], colors=['yellow', 'red', 'blue'])
plt.title('COVID-19 Cases Trend in Delhi (14-Mar-2020 to 05-Sept-2020)')
plt.ylabel('Number of Cases')
plt.legend(loc='upper left')
plt.show()

# Plotting Active COVID-19 Cases Trend in Delhi
active_cases_data = []

for date in delhi_data['date'].unique():
    active = (
        delhi_data[(delhi_data['date'] == date) & (delhi_data['status'] == 'Confirmed')]['dl'].astype(int).sum()
        - delhi_data[(delhi_data['date'] == date) & (delhi_data['status'] == 'Recovered')]['dl'].astype(int).sum()
        - delhi_data[(delhi_data['date'] == date) & (delhi_data['status'] == 'Deceased')]['dl'].astype(int).sum()
    )
    active_cases_data.append(active)

plt.figure(figsize=(14, 8))
plt.stackplot(delhi_data['date'].unique(), active_cases_data, labels=['Active Cases'], colors=['#FFA500'])
plt.title('Active COVID-19 Cases Trend in Delhi (14-Mar-2020 to 05-Sept-2020)')
plt.ylabel('Number of Active Cases')
plt.legend(loc='upper left')
plt.show()


delhi_data = delhi_data[['date', 'status', 'dl']]


delhi_data['days_since_start'] = (delhi_data['date'] - pd.to_datetime(sDate_2)).dt.days
delhi_data['dl'] = delhi_data['dl'].astype(int)


confirmed_data = delhi_data[delhi_data['status'] == 'Confirmed']
recovered_data = delhi_data[delhi_data['status'] == 'Recovered']
deceased_data = delhi_data[delhi_data['status'] == 'Deceased']


def perform_linear_regression(x, y):
    model = LinearRegression()
    model.fit(x, y)
    intercept = model.intercept_
    slope = model.coef_[0]
    return intercept, slope


x_confirmed = confirmed_data['days_since_start'].values.reshape(-1, 1)
y_confirmed = confirmed_data['dl'].values

x_recovered = recovered_data['days_since_start'].values.reshape(-1, 1)
y_recovered = recovered_data['dl'].values

x_deceased = deceased_data['days_since_start'].values.reshape(-1, 1)
y_deceased = deceased_data['dl'].values

confirmed_intercept, confirmed_slope = perform_linear_regression(x_confirmed, y_confirmed)
recovered_intercept, recovered_slope = perform_linear_regression(x_recovered, y_recovered)
deceased_intercept, deceased_slope = perform_linear_regression(x_deceased, y_deceased)


print(f"Linear Regression for Delhi - Confirmed cases: Intercept = {confirmed_intercept}, Slope = {confirmed_slope}")
print(f"Linear Regression for Delhi - Recovered cases: Intercept = {recovered_intercept}, Slope = {recovered_slope}")
print(f"Linear Regression for Delhi - Deceased cases: Intercept = {deceased_intercept}, Slope = {deceased_slope}")


plt.figure(figsize=(14, 8))


plt.subplot(3, 1, 1)
plt.scatter(x_confirmed, y_confirmed, color='blue')
plt.plot(x_confirmed, confirmed_intercept + confirmed_slope * x_confirmed, color='red')
plt.title('Linear Regression - Confirmed Cases in Delhi')
plt.xlabel('Days Since Start')
plt.ylabel('Confirmed Cases')

plt.subplot(3, 1, 2)
plt.scatter(x_recovered, y_recovered, color='green')
plt.plot(x_recovered, recovered_intercept + recovered_slope * x_recovered, color='red')
plt.title('Linear Regression - Recovered Cases in Delhi')
plt.xlabel('Days Since Start')
plt.ylabel('Recovered Cases')


plt.subplot(3, 1, 3)
plt.scatter(x_deceased, y_deceased, color='purple')
plt.plot(x_deceased, deceased_intercept + deceased_slope * x_deceased, color='red')
plt.title('Linear Regression - Deceased Cases in Delhi')
plt.xlabel('Days Since Start')
plt.ylabel('Deceased Cases')

plt.tight_layout()
plt.show()