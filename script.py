import datetime
import requests
import os

# CONFIGURATION: Add your locations here (Latitude, Longitude)
# To add Place 2 or Place 3, replace None with numbers (e.g., 52.52, 13.40)
PLACES = [
    {"lat": 51.5042, "lon": 0.0500}, # Place 1: London City Airport
    {"lat": None, "lon": None},      # Place 2
    {"lat": None, "lon": None}       # Place 3
]

FILENAME = "weather_data.csv"

def get_weather(lat, lon):
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

# Fetch data
now = datetime.datetime.now()
c_date, c_time = now.strftime("%Y-%m-%d"), now.strftime("%H:%M")
p1_t, p1_da, p1_sd = get_weather(PLACES[0]["lat"], PLACES[0]["lon"])
p2_t, p2_da, p2_sd = get_weather(PLACES[1]["lat"], PLACES[1]["lon"])
p3_t, p3_da, p3_sd = get_weather(PLACES[2]["lat"], PLACES[2]["lon"])

# Build the exact columns (A to S)
row = [
    c_date, c_time,
    p1_t[0], p1_t[1], p2_t[0], p2_t[1], p3_t[0], p3_t[1], # Tomorrow
    p1_da[0], p1_da[1], p2_da[0], p2_da[1], p3_da[0], p3_da[1], # Day After
    p1_sd[0], p1_sd[1], p2_sd[0], p2_sd[1], p3_sd[0], p3_sd[1], # 2nd Day After
    f"Updated at {c_time}" # Status column
]
row_str = ",".join(["" if v is None else str(v) for v in row]) + "\n"

# Create file with headers if it doesn't exist
if not os.path.exists(FILENAME):
    headers = "Date,Time,P1_T1,P1_H1,P2_T1,P2_H1,P3_T1,P3_H1,P1_T2,P1_H2,P2_T2,P2_H2,P3_T2,P3_H2,P1_T3,P1_H3,P2_T3,P2_H3,P3_T3,P3_H3,Status\n"
    with open(FILENAME, "w") as f: f.write(headers)

# Read file, append new data, and keep maximum 30 days of data (720 hourly entries)
with open(FILENAME, "r") as f: lines = f.readlines()
lines.append(row_str)
if len(lines) > 721: lines = [lines[0]] + lines[-720:] # Keep headers + last 720 rows
with open(FILENAME, "w") as f: f.writelines(lines)
