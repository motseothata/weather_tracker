import datetime
import requests
import os

PLACES = [
    {"lat": 51.5042, "lon": 0.0500}, # Place 1: London City Airport
    {"lat": None, "lon": None},      # Place 2
    {"lat": None, "lon": None}       # Place 3
]

FILENAME = "weather_data.csv"

def get_weather(lat, lon):
    if lat is None or lon is None:
        return (None, None), (None, None), (None, None), (None, None)
    try:
        # past_days=1 includes yesterday's finalized data in the results
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,relative_humidity_2m_max&past_days=1&timezone=Europe%2FLondon"
        res = requests.get(url).json()
        
        # With past_days=1: 
        # Index 0 = Yesterday, Index 1 = Today, Index 2 = Tomorrow, Index 3 = Day After, Index 4 = 2nd Day After
        yesterday_actual = (res['daily']['temperature_2m_max'][0], res['daily']['relative_humidity_2m_max'][0])
        tomorrow_pred = (res['daily']['temperature_2m_max'][2], res['daily']['relative_humidity_2m_max'][2])
        day_after_pred = (res['daily']['temperature_2m_max'][3], res['daily']['relative_humidity_2m_max'][3])
        sec_day_pred = (res['daily']['temperature_2m_max'][4], res['daily']['relative_humidity_2m_max'][4])
        
        return yesterday_actual, tomorrow_pred, day_after_pred, sec_day_pred
    except:
        return (None, None), (None, None), (None, None), (None, None)

# 1. Fetch current time and weather data strings
now = datetime.datetime.now()
yesterday_date = (now - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
c_date, c_time = now.strftime("%Y-%m-%d"), now.strftime("%H:%M")

p1_yest, p1_tom, p1_da, p1_sd = get_weather(PLACES[0]["lat"], PLACES[0]["lon"])
_, p2_tom, p2_da, p2_sd = get_weather(PLACES[1]["lat"], PLACES[1]["lon"])
_, p3_tom, p3_da, p3_sd = get_weather(PLACES[2]["lat"], PLACES[2]["lon"])

# 2. Prepare the new hourly row (Leave Actuals blank for now)
new_row = [
    c_date, c_time,
    p1_tom[0], p1_tom[1], p2_tom[0], p2_tom[1], p3_tom[0], p3_tom[1],       # Tomorrow
    p1_da[0], p1_da[1], p2_da[0], p2_da[1], p3_da[0], p3_da[1],             # Day After
    p1_sd[0], p1_sd[1], p2_sd[0], p2_sd[1], p3_sd[0], p3_sd[1],             # 2nd Day After
    "", ""                                                                  # Actual Max T, Actual Max H (Filled tomorrow)
]
new_row_str = ",".join(["" if v is None else str(v) for v in new_row]) + "\n"

# Create file with headers if it doesn't exist yet
if not os.path.exists(FILENAME):
    headers = "Date,Time,P1_T1,P1_H1,P2_T1,P2_H1,P3_T1,P3_H1,P1_T2,P1_H2,P2_T2,P2_H2,P3_T2,P3_H2,P1_T3,P1_H3,P2_T3,P2_H3,P3_T3,P3_H3,Actual_Max_T,Actual_Max_H\n"
    with open(FILENAME, "w") as f: f.write(headers)

# 3. Read existing data and update yesterday's rows with the final actual values
with open(FILENAME, "r") as f: 
    lines = f.readlines()

updated_lines = [lines[0]] # Keep the header row
for line in lines[1:]:
    columns = line.strip().split(",")
    # If this row belongs to yesterday, update its last two columns with finalized actual max data
    if columns[0] == yesterday_date and p1_yest[0] is not None:
        columns[-2] = str(p1_yest[0]) # Actual Max Temp
        columns[-1] = str(p1_yest[1]) # Actual Max Humid
    updated_lines.append(",".join(columns) + "\n")

# Append today's new data row
updated_lines.append(new_row_str)

# Maintain 30-day limit (720 hourly entries max)
if len(updated_lines) > 721: 
    updated_lines = [updated_lines[0]] + updated_lines[-720:]

# Write everything back down
with open(FILENAME, "w") as f: 
    f.writelines(updated_lines)
