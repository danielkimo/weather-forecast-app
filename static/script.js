const form = document.getElementById("search-form");
const input = document.getElementById("city-input");
const statusEl = document.getElementById("status");
const resultEl = document.getElementById("result");

const locationNameEl = document.getElementById("location-name");
const currentIconEl = document.getElementById("current-icon");
const currentTempEl = document.getElementById("current-temp");
const currentDescEl = document.getElementById("current-desc");
const feelsLikeEl = document.getElementById("feels-like");
const humidityEl = document.getElementById("humidity");
const windEl = document.getElementById("wind");
const forecastEl = document.getElementById("forecast");

function setStatus(message, isError = false) {
  statusEl.textContent = message;
  statusEl.classList.toggle("error", isError);
}

function formatDate(dateStr) {
  const date = new Date(dateStr);
  return date.toLocaleDateString(undefined, { weekday: "short", month: "short", day: "numeric" });
}

async function fetchWeather(city) {
  setStatus("Loading...");
  resultEl.classList.add("hidden");

  try {
    const res = await fetch(`/api/weather?city=${encodeURIComponent(city)}`);
    const data = await res.json();

    if (!res.ok) {
      setStatus(data.error || "Something went wrong.", true);
      return;
    }

    renderWeather(data);
    setStatus("");
  } catch (err) {
    setStatus("Network error. Please try again.", true);
  }
}

function renderWeather(data) {
  const { location, current, forecast } = data;

  const locationParts = [location.name, location.admin1, location.country].filter(Boolean);
  locationNameEl.textContent = locationParts.join(", ");

  currentIconEl.textContent = current.icon;
  currentTempEl.textContent = `${Math.round(current.temperature)}°C`;
  currentDescEl.textContent = current.description;
  feelsLikeEl.textContent = `Feels like ${Math.round(current.apparent_temperature)}°C`;
  humidityEl.textContent = `Humidity ${current.humidity}%`;
  windEl.textContent = `Wind ${current.wind_speed} km/h`;

  forecastEl.innerHTML = "";
  forecast.forEach((day) => {
    const card = document.createElement("div");
    card.className = "forecast-day";
    card.innerHTML = `
      <div class="date">${formatDate(day.date)}</div>
      <span class="icon">${day.icon}</span>
      <div class="range">${Math.round(day.max)}° / ${Math.round(day.min)}°</div>
    `;
    forecastEl.appendChild(card);
  });

  resultEl.classList.remove("hidden");
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const city = input.value.trim();
  if (city) {
    fetchWeather(city);
  }
});

// Default lookup on load.
window.addEventListener("DOMContentLoaded", () => {
  input.value = "Taipei";
  fetchWeather("Taipei");
});
