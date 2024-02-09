from datetime import datetime

from ..api_client.greenness_forecast import GreennessForecast

class CurrentNextForecastResult:
  current: GreennessForecast
  next: GreennessForecast

  def __init__(self, current, next):
    self.current = current
    self.next = next

def get_current_and_next_forecast(current: datetime, forecast: list[GreennessForecast], restrict_highlighted = False):
  if (forecast is not None):
    current_forecast: GreennessForecast = None
    next_forecast: GreennessForecast = None

    for item in forecast:
      if restrict_highlighted and item.highlight_flag == False:
        continue

      if (item.start <= current and item.end >= current):
        current_forecast = item

      if item.start > current and (next_forecast is None or next_forecast.start > item.start):
        next_forecast = item

    return CurrentNextForecastResult(current_forecast, next_forecast)
  
def greenness_forecast_to_dictionary(forecast: GreennessForecast):
  if forecast is not None:
    return {
      "start": forecast.start,
      "end": forecast.end,
      "greenness_index": forecast.greenness_index,
      "greenness_score": forecast.greenness_score,
      "is_highlighted": forecast.highlight_flag
    }
  
  return {}
  
def greenness_forecast_to_dictionary_list(forecast: list[GreennessForecast]):
  items = []
  if (forecast is not None):
    for item in forecast:
      items.append(greenness_forecast_to_dictionary(item))

  return items