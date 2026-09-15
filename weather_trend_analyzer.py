"""
Weather Trend Analyzer
-----------------------
Fetches recent daily weather data for a chosen city using the free,
key-free Open-Meteo API, analyzes temperature trends with pandas/numpy,
and visualizes the results with matplotlib.

Tech stack: requests, pandas, numpy, matplotlib
No API key required.
"""

import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# A few example cities with their coordinates.
# Add more cities here if you want to analyze other locations.
CITIES = {
    "Delhi": (28.6139, 77.2090),
    "Mumbai": (19.0760, 72.8777),
    "Gurugram": (28.4595, 77.0266),
}


def fetch_weather_data(latitude, longitude, past_days=16):
    """
    Fetch daily max/min temperature and precipitation for the last
    `past_days` days from the Open-Meteo API.
    Returns the raw JSON response.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "past_days": past_days,
        "forecast_days": 1,
        "timezone": "auto",
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def to_dataframe(weather_json):
    """
    Convert the Open-Meteo JSON response into a clean pandas DataFrame
    with one row per day.
    """
    daily = weather_json["daily"]
    df = pd.DataFrame({
        "date": pd.to_datetime(daily["time"]),
        "temp_max": daily["temperature_2m_max"],
        "temp_min": daily["temperature_2m_min"],
        "precipitation": daily["precipitation_sum"],
    })
    # Derived column: average temperature for the day
    df["temp_avg"] = (df["temp_max"] + df["temp_min"]) / 2
    return df


def compute_stats(df):
    """
    Use numpy to compute basic summary statistics for the temperature data.
    Returns a dictionary of stats.
    """
    return {
        "mean_temp": np.mean(df["temp_avg"]),
        "max_temp": np.max(df["temp_max"]),
        "min_temp": np.min(df["temp_min"]),
        "std_dev_temp": np.std(df["temp_avg"]),
        "total_precipitation": np.sum(df["precipitation"]),
        "rainy_days": int(np.sum(df["precipitation"] > 0)),
    }


def plot_trends(df, city_name, save_path="weather_trend.png"):
    """
    Plot max/min/avg temperature trend and precipitation for the period.
    Saves the chart as a PNG file.
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7), sharex=True)

    ax1.plot(df["date"], df["temp_max"], label="Max Temp (°C)", color="#e74c3c")
    ax1.plot(df["date"], df["temp_min"], label="Min Temp (°C)", color="#3498db")
    ax1.plot(df["date"], df["temp_avg"], label="Avg Temp (°C)", color="#2c3e50", linestyle="--")
    ax1.set_ylabel("Temperature (°C)")
    ax1.set_title(f"Temperature Trend — {city_name} (last {len(df)} days)")
    ax1.legend()
    ax1.grid(alpha=0.3)

    ax2.bar(df["date"], df["precipitation"], color="#2980b9")
    ax2.set_ylabel("Precipitation (mm)")
    ax2.set_xlabel("Date")
    ax2.set_title("Daily Precipitation")
    ax2.grid(alpha=0.3)

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    print(f"Chart saved to {save_path}")


def main():
    city_name = "Delhi"
    lat, lon = CITIES[city_name]

    print(f"Fetching weather data for {city_name}...")
    raw_data = fetch_weather_data(lat, lon)
    df = to_dataframe(raw_data)

    stats = compute_stats(df)
    print("\n--- Weather Summary ---")
    print(f"Average temperature : {stats['mean_temp']:.1f} °C")
    print(f"Highest temperature : {stats['max_temp']:.1f} °C")
    print(f"Lowest temperature  : {stats['min_temp']:.1f} °C")
    print(f"Temperature std dev : {stats['std_dev_temp']:.2f}")
    print(f"Total precipitation : {stats['total_precipitation']:.1f} mm")
    print(f"Rainy days          : {stats['rainy_days']}")

    plot_trends(df, city_name)


if __name__ == "__main__":
    main()
