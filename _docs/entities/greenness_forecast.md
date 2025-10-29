# Greenness Forecast

To support the [greener nights](https://octopus.energy/smart/greener-nights/) supported by Octopus Energy, the following entities are provided.

## Current Index

`sensor.octopus_energy_{{ACCOUNT_ID}}_greenness_forecast_current_index`

The greenness index for the current period.

!!! note
    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them). 

!!! info
    If you are wanting a nice way to display the upcoming forecast, then why not try a [community card](../community.md#greenness-forecast)?

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The time the current forecast period started |
| `end` | `datetime` | The time the current forecast period ends |
| `greenness_index` | `int` | The index for the current forecast |
| `greenness_score` | `string` | The score associated by Octopus Energy for the current forecast |
| `is_highlighted` | `bool` | Determines if the current forecast has been highlighted by Octopus Energy |
| `next_start` | `datetime` | The time the next forecast period starts |
| `next_end` | `datetime` | The time the next forecast period ends |
| `forecast` | `array` | The entire upcoming forecast |

For each forecast item, the following attributes are provided

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The time the current forecast period started |
| `end` | `datetime` | The time the current forecast period ends |
| `greenness_index` | `int` | The index for the current forecast |
| `greenness_score` | `string` | The score associated by Octopus Energy for the current forecast |
| `is_highlighted` | `bool` | Determines if the current forecast has been highlighted by Octopus Energy |

!!! info

    You can use the [data_last_retrieved sensor](./diagnostics.md#greenness-forecast-data-last-retrieved) to determine when the underlying data was last retrieved from the OE servers.

## Next Index

`sensor.octopus_energy_{{ACCOUNT_ID}}_greenness_forecast_next_index`

The greenness index for the next period.

!!! note
    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them). 

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The time the next forecast period started |
| `end` | `datetime` | The time the next forecast period ends |
| `greenness_index` | `int` | The index for the next forecast |
| `greenness_score` | `string` | The score associated by Octopus Energy for the next forecast |
| `is_highlighted` | `bool` | Determines if the next forecast has been highlighted by Octopus Energy |

!!! info

    You can use the [data_last_retrieved sensor](./diagnostics.md#greenness-forecast-data-last-retrieved) to determine when the underlying data was last retrieved from the OE servers.

## Highlighted

`binary_sensor.octopus_energy_{{ACCOUNT_ID}}_greenness_forecast_highlighted`

Determines if the current greenness forecast has been highlighted by OE as the greenest for the current forecast.

!!! note
    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them). 

| Attribute | Type | Description |
|-----------|------|-------------|
| `current` | `object` | The details of the currently highlighted forecast |
| `next_start` | `datetime` | The time the next highlighted forecast period starts |
| `next_end` | `datetime` | The time the next highlighted forecast period ends |

For `current`, the following attributes are provided

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The time the current forecast period started |
| `end` | `datetime` | The time the current forecast period ends |
| `greenness_index` | `int` | The index for the current forecast |
| `greenness_score` | `string` | The score associated by Octopus Energy for the current forecast |
| `is_highlighted` | `bool` | Determines if the current forecast has been highlighted by Octopus Energy |

!!! info

    You can use the [data_last_retrieved sensor](./diagnostics.md#greenness-forecast-data-last-retrieved) to determine when the underlying data was last retrieved from the OE servers.

## Greener Nights Calendar

`calendar.octopus_energy_{{ACCOUNT_ID}}_greener_nights`

Read only [calendar](https://www.home-assistant.io/integrations/calendar) sensor to record nights that are highlighted as "greener nights". Will be `on` when a greener night is active. Calendar events will be automatically added/removed by the integration when greener nights are discovered. 

Standard calendar attributes will indicate the current/next highlighted greener night.

!!! warning

    The sensor does not store past events indefinitely. Past events could be removed without notice.

!!! info

    You can use the [data_last_retrieved sensor](./diagnostics.md#greenness-forecast-data-last-retrieved) to determine when the underlying data was last retrieved from the OE servers.

| Attribute | Type | Description |
|-----------|------|-------------|
| `greenness_index` | `int` | The index for the current/next forecast |
| `greenness_score` | `string` | The score associated by Octopus Energy for the current/next forecast |

### Automation Example

Below is an example of raising a persistent notification 5 minutes before a greener night starts.

```yaml
triggers:
- trigger: calendar
  entity_id: calendar.octopus_energy_{{ACCOUNT_ID}}_greener_nights
  event: start
  offset: -00:05:00
actions:
- action: persistent_notification.create
  data:
    title: Greener Night Starting
    message: >
      {% set minutes = ((state_attr(trigger.entity_id, 'end_time') | as_datetime - state_attr(trigger.entity_id, 'start_time') | as_datetime).seconds / 60) | round(0) | string %}
      {% set start_time = (state_attr(trigger.entity_id, 'start_time') | as_datetime).strftime('%H:%M') %}
      Greener night starts at {{ start_time }} for {{ minutes }} minutes.
```