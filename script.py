import datetime
import requests
import os

PLACES = [
    {"lat": 51.5042, "lon": 0.0500}, # Place 1: London City Airport
    {"lat": None, "lon": None},      # Place 2
    {"lat": None, "lon": None}       # Place 3
]

FILENAME = "weather_data.csv"

def get_historical_actuals(lat, lon, target_date_str):
    if lat is None or lon is None:
        return "", ""
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&start_date={target_date_str}&end_date={target_date_str}&daily=temperature_2m_max,relative_humidity_2m_max&timezone=Europe%2FLondon"
        res = requests.get(url).json()
        return str(res['daily']['temperature_2m_max'][0]), str(res['daily']['relative_humidity_2m_max'][0])
    except:
        return "", ""

def get_forecasts(lat, lon):
    if lat is None or lon is None:
        return (None, None), (None, None), (None, None)
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,relative_humidity_2m_max&timezone=Europe%2FLondon"
        res = requests.get(url).json()
        tom = (res['daily']['temperature_2m_max'][1], res['daily']['relative_humidity_2m_max'][1])
        da = (res['daily']['temperature_2m_max'][2], res['daily']['relative_humidity_2m_max'][2])
        sd = (res['daily']['temperature_2m_max'][3], res['daily']['relative_humidity_2m_max'][3])
        return tom, da, sd
    except:
        return (None, None), (None, None), (None, None)

# 1. Date math
now = datetime.datetime.now()
c_date, c_time = now.strftime("%Y-%m-%d"), now.strftime("%H:%M")
yesterday_date = (now - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

# 2. Extract upcoming values
p1_tom, p1_da, p1_sd = get_forecasts(PLACES[0]["lat"], PLACES[0]["lon"])
p2_tom, p2_da, p2_sd = get_forecasts(PLACES[1]["lat"], PLACES[1]["lon"])
p3_tom, p3_da, p3_sd = get_forecasts(PLACES[2]["lat"], PLACES[2]["lon"])

# Build row mapping from Column A to V
new_row = [
    c_date, c_time,
    p1_tom[0], p1_tom[1], p2_tom[0], p2_tom[1], p3_tom[0], p3_tom[1],
    p1_da[0], p1_da[1], p2_da[0], p2_da[1], p3_da[0], p3_da[1],
    p1_sd[0], p1_sd[1], p2_sd[0], p2_sd[1], p3_sd[0], p3_sd[1],
    "", ""  # Status_T (U) and Status_H (V) start empty
]
new_row_str = ",".join(["" if v is None else str(v) for v in new_row]) + "\n"

if not os.path.exists(FILENAME):
    headers = "Date,Time,P1_T1,P1_H1,P2_T1,P2_H1,P3_T1,P3_H1,P1_T2,P1_H2,P2_T2,P2_H2,P3_T2,P3_H2,P1_T3,P1_H3,P2_T3,P2_H3,P3_T3,P3_H3,Status_T,Status_H\n"
    with open(FILENAME, "w") as f: f.write(headers)

# 3. Process historical loops cleanly
with open(FILENAME, "r") as f:
    lines = f.readlines()

yest_t, yest_h = get_historical_actuals(PLACES[0]["lat"], PLACES[0]["lon"], yesterday_date)

updated_lines = [lines[0]]
for line in lines[1:]:
    cols = line.strip().split(",")
    # Update yesterday's entries exclusively
    if cols[0] == yesterday_date and yest_t and yest_h:
        if len(cols) >= 22:
            cols[-2] = yest_t
            cols[-1] = yest_h
    updated_lines.append(",".join(cols) + "\n")

updated_lines.append(new_row_str)

# 1-Year Capacity cap
if len(updated_lines) > 8761:
    updated_lines = [updated_lines[0]] + updated_lines[-8760:]

with open(FILENAME, "w") as f:
    f.writelines(updated_lines)
