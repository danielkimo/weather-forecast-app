# Weather App

A simple weather lookup web app built with Flask, powered by the free
[Open-Meteo](https://open-meteo.com/) geocoding and forecast APIs (no API key required).

## Features
- Search current weather by city name
- Shows temperature, feels-like, humidity, wind speed, and condition
- 5-day forecast with high/low temperatures

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open http://localhost:5050 in your browser.

## Tech Stack
- Backend: Flask (Python)
- Frontend: Vanilla HTML/CSS/JavaScript
- Weather data: Open-Meteo API
